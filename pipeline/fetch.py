"""Zero-token discovery: pull all structured sources, keep only NEW relevant DACH postings,
write them as small batches to inbox/<date>/ for LLM extraction.

Also (free, no LLM): bumps last_seen/status of known jobs, records which companies
were fetched, and auto-adds newly discovered employers to companies.csv so the
registry keeps growing run after run.
"""
import datetime as dt, json, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from .common import (INBOX, JOBS_CSV, JOB_FIELDS, SEEN_JSON, ENTRY, COMPANY_EXCLUDE, STAFFING, is_relevant_text, canon_url, country_of, is_dach,
                     is_relevant_title, load_json, make_job_id, read_csv, save_json, trim_description, write_csv)
from . import ats, boards, companies as reg

BATCH = 30
DONE_STATES = ("ingested", "rejected")
BOARD_SOURCES = ("Bundesagentur für Arbeit API", "Arbeitnow API", "karriere.at")
PER_COMPANY = 3          # max new postings per company per run (diversity > volume for skill stats)

def priority(p, country_counts):
    """Higher = extract first. Rewards what the dataset lacks (entry level, CH/AT, original
    company postings, salary info) and penalises staffing agencies."""
    s = 0.0
    if p.get("entry_level_hint"): s += 3
    s += {"Switzerland": 3, "Austria": 2}.get(p.get("country"), 0)
    if not p["source"].startswith(("Arbeitnow", "Bundesagentur", "karriere")): s += 2   # own ATS / web
    if p.get("salary_text") or "€" in p["text"] or "EUR" in p["text"] or "CHF" in p["text"]: s += 1
    if STAFFING.search(p.get("company", "")): s -= 4
    s -= 0.001 * country_counts.get(p.get("country"), 0)
    return s

def _fetch_company(r):
    fn = ats.ADAPTERS.get(r["ats"])
    if not fn:
        return r, None
    try:
        return r, fn(r["ats_slug"], r["company"])
    except Exception:
        return r, None

def _resolve_detail(p):
    """Fill description (and for karriere.at: company/location/salary) lazily."""
    try:
        if "_detail_full" in p:
            full = p.pop("_detail_full")() or {}
            for k in ("company", "location", "description", "posted", "salary_text", "remote"):
                if full.get(k):
                    p[k] = full[k]
        if "_detail" in p:
            fn = p.pop("_detail")
            if not p.get("description"):
                p["description"] = fn() or ""
    except Exception:
        pass
    p.pop("_detail", None); p.pop("_detail_full", None)
    return p

def run(date=None, sources=("ats", "arbeitnow", "ba", "karriere"), stale_days=0, max_companies=None,
        workers=12, dry=False, max_new=200):
    today = date or dt.date.today().isoformat()
    seen = load_json(SEEN_JSON, {})
    jobs = read_csv(JOBS_CSV)
    job_ids = {j["job_id"] for j in jobs}
    url_to_job = {canon_url(j["posting_url"]): j for j in jobs}
    id_to_job = {j["job_id"]: j for j in jobs}
    regrows = reg.load()
    log, raw = [], []
    fetched_sources_ok = set()        # sources with a complete listing (for open/closed status)

    # ---- company ATS feeds
    if "ats" in sources:
        todo = [r for r in regrows if r.get("ats") and r.get("ats_slug")]
        if stale_days:
            cutoff = (dt.date.fromisoformat(today) - dt.timedelta(days=stale_days)).isoformat()
            todo = [r for r in todo if (r.get("last_fetched") or "") < cutoff]
        todo.sort(key=lambda r: r.get("last_fetched") or "")      # oldest first
        if max_companies:
            todo = todo[:max_companies]
        ok = fail = 0
        with ThreadPoolExecutor(workers) as ex:
            for fut in as_completed([ex.submit(_fetch_company, r) for r in todo]):
                r, posts = fut.result()
                if posts is None:
                    fail += 1; r["notes"] = (f"feed failed {today}; " + r.get("notes", ""))[:200]; continue
                ok += 1
                rel = [p for p in posts if is_relevant_title(p["title"]) and is_dach(p["location"], remote_ok=True)]
                r["last_fetched"], r["relevant_open"] = today, str(len(rel))
                r["relevant_total"] = str(max(int(r.get("relevant_total") or 0), len(rel)))
                for p in rel:
                    p["company"] = r["company"]          # registry name = canonical company
                raw += rel
                if posts:
                    fetched_sources_ok.add(posts[0]["source"])
        log.append(f"ATS feeds: {ok} ok, {fail} failed, of {len(todo)} companies")

    # ---- job boards
    board_fns = {"arbeitnow": boards.arbeitnow, "ba": boards.arbeitsagentur, "karriere": boards.karriere}
    for name, fn in board_fns.items():
        if name not in sources:
            continue
        try:
            posts = fn()
        except Exception as e:
            log.append(f"{name}: FAILED ({type(e).__name__})"); continue
        rel = [p for p in posts if is_relevant_title(p["title"]) and not COMPANY_EXCLUDE.search(p.get("company", ""))]
        log.append(f"{name}: {len(posts)} listed, {len(rel)} relevant by title")
        raw += rel

    # ---- dedupe against seen + jobs.csv, bump last_seen of known jobs
    fresh, bumped, by_key = [], 0, {}
    for p in raw:
        cu = canon_url(p["url"])
        if not cu:
            continue
        known = url_to_job.get(cu) or (id_to_job.get(make_job_id(p["company"], p["title"], p["location"]))
                                        if p["company"] else None)
        if known:
            known["last_seen_date"], known["status"] = today, "open"; bumped += 1
            continue
        s = seen.get(cu)
        if s and s.get("state") in DONE_STATES:
            s["last"] = today
            continue
        by_key.setdefault(cu, p)
    fresh = list(by_key.values())

    # ---- lazy detail fetch only for survivors
    with ThreadPoolExecutor(workers) as ex:
        fresh = list(ex.map(_resolve_detail, fresh))
    # karriere.at listings only learn company/location after detail; re-check now
    out, no_text, off_topic = [], 0, 0
    for p in fresh:
        if not is_dach(p["location"], remote_ok=True):
            seen[canon_url(p["url"])] = {"state": "rejected", "why": "not DACH", "first": today, "last": today}
            continue
        jid = make_job_id(p["company"], p["title"], p["location"])
        if jid in job_ids:
            continue
        job_ids.add(jid)
        p["job_id"], p["country"] = jid, country_of(p["location"])
        p["entry_level_hint"] = bool(ENTRY.search(p["title"]))
        p["text"] = trim_description(p.pop("description", ""))
        if len(p["text"]) < 300:          # nothing to extract skills from; retried next run
            no_text += 1; job_ids.discard(jid); continue
        # AMS jobs syndicated into the BA feed (ref 11949-…) carry a generic occupation as title
        # (e.g. 'Data Engineer' for security roles) -> require data/ML terms in the body.
        if "/jobdetail/11949-" in p["url"] and not is_relevant_text(p["text"]):
            seen[canon_url(p["url"])] = {"state": "rejected", "why": "no data/ML terms in text",
                                         "first": today, "last": today}
            off_topic += 1; job_ids.discard(jid); continue
        out.append(p)

    # ---- budget: rank, cap per company, cap total. Leftovers are NOT marked seen -> next run.
    cc = {}
    for p in out:
        cc[p["country"]] = cc.get(p["country"], 0) + 1
    out.sort(key=lambda p: -priority(p, cc))
    per, kept = {}, []
    for p in out:
        k = p["company"].lower()
        if per.get(k, 0) >= PER_COMPANY:
            continue
        per[k] = per.get(k, 0) + 1
        kept.append(p)
    backlog = len(out) - min(len(kept), max_new)
    out = kept[:max_new]

    # ---- closed detection for complete ATS listings
    open_urls = {canon_url(p["url"]) for p in raw}
    closed = 0
    for j in jobs:
        if j.get("source") in fetched_sources_ok and canon_url(j["posting_url"]) not in open_urls \
                and j.get("status") != "closed":
            j["status"] = "closed"; closed += 1

    # ---- auto-grow the company registry from board postings
    grown = 0
    for p in kept:
        if p["source"] in ("Arbeitnow API", "Bundesagentur für Arbeit API", "karriere.at") and p["company"] \
                and not STAFFING.search(p["company"]):
            _, created = reg.add(regrows, p["company"], country=p["country"], via=f"board:{p['source']}")
            grown += created

    # ---- write inbox batches
    d = INBOX / today
    if not dry:
        d.mkdir(parents=True, exist_ok=True)
        if any(d.glob("batch_*.out.jsonl")):
            raise SystemExit(f"{d} already has extraction output — run `jobs.py ingest --date {today}` first, "
                             f"or fetch with another --date. Refusing to overwrite.")
        for f in d.glob("batch_[0-9]*.jsonl"):
            f.unlink()
        for i in range(0, len(out), BATCH):
            with open(d / f"batch_{i // BATCH + 1:02d}.jsonl", "w", encoding="utf-8") as f:
                for p in out[i:i + BATCH]:
                    f.write(json.dumps(p, ensure_ascii=False) + "\n")
        for p in out:
            seen[canon_url(p["url"])] = {"state": "pending", "first": today, "last": today, "job_id": p["job_id"]}
        save_json(SEEN_JSON, seen)
        reg.save(regrows)
        write_csv(JOBS_CSV, jobs, JOB_FIELDS)

    chars = sum(len(p["text"]) for p in out)
    summary = {"date": today, "new_postings": len(out), "backlog_left_for_next_run": backlog,
               "dropped_no_text": no_text, "dropped_off_topic": off_topic, "batches": -(-len(out) // BATCH),
               "known_jobs_reseen": bumped, "marked_closed": closed, "companies_added": grown,
               "approx_input_tokens": chars // 4, "log": log,
               "by_source": _count(out, "source"), "by_country": _count(out, "country")}
    if not dry:
        (d / "manifest.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1))
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return summary

def _count(rows, k):
    c = {}
    for r in rows:
        key = r.get(k) or "?"
        key = key.split(" (")[0]
        c[key] = c.get(key, 0) + 1
    return dict(sorted(c.items(), key=lambda x: -x[1]))
