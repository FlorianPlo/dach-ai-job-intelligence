#!/usr/bin/env python3
"""Single entry point for the DACH job-intelligence pipeline.

  python3 jobs.py fetch [--date D] [--max-new 200] [--sources ats,arbeitnow,ba,karriere] [--stale-days N] [--only A,B]
  python3 jobs.py add-url URL [URL ...] [--date D]      # queue postings found by web search
  python3 jobs.py ingest [--date D]                     # merge LLM extractions into jobs.csv
  python3 jobs.py analyze [--date D]                    # regenerate the three reports
  python3 jobs.py import-companies FILE                 # bulk import (CSV/TSV/TXT)
  python3 jobs.py add-company NAME [--domain d] [--careers URL] [--country C] [--ats A --slug S]
  python3 jobs.py detect [--limit N] [--workers N] [--only NAME]   # find each company's ATS feed
  python3 jobs.py queries [--n 15]                      # next web-search queries to try
  python3 jobs.py log-query "QUERY" --found N
  python3 jobs.py check-active [--older-than 30]        # re-check postings not seen recently -> status
  python3 jobs.py status                                # registry / inbox / coverage overview
"""
import argparse, datetime as dt, json, subprocess, sys
from pipeline import companies as reg, fetch, ingest, queries
from pipeline.common import INBOX, JOBS_CSV, SEEN_JSON, canon_url, country_of, is_dach, load_json, make_job_id, \
    read_csv, save_json, trim_description, http, html_to_text
from pipeline.ats import _page_full

def add_url(urls, date):
    """Fetch postings found via web search; JSON-LD first (compact), else trimmed page text."""
    d = INBOX / date; d.mkdir(parents=True, exist_ok=True)
    seen = load_json(SEEN_JSON, {})
    known = {canon_url(j["posting_url"]) for j in read_csv(JOBS_CSV)}
    f = d / "batch_web.jsonl"
    queued = {json.loads(l)["url"] for l in f.read_text().splitlines() if l.strip()} if f.exists() else set()
    n = 0
    with open(f, "a", encoding="utf-8") as out:
        for u in urls:
            cu = canon_url(u)
            if cu in known or seen.get(cu, {}).get("state") in ("ingested", "rejected") or u in queued:
                print(f"skip (known): {u}"); continue
            full = _page_full(u)          # JSON-LD if it has a description, else page text + <h1>
            if not full.get("description"):
                print(f"FAILED: {u}"); continue
            p = {"company": "", "title": "", "location": "", "url": u, "posted": "", "remote": False,
                 "salary_text": "", **full}
            p["source"] = "web search"
            p["country"] = country_of(p["location"])
            p["job_id"] = make_job_id(p["company"], p["title"], p["location"]) if p["company"] else ""
            p["text"] = trim_description(p.pop("description", ""), limit=6000)
            out.write(json.dumps(p, ensure_ascii=False) + "\n")
            seen[cu] = {"state": "pending", "first": date, "last": date}
            n += 1
            print(f"queued: {p.get('company') or '?'} — {p.get('title') or u}")
    save_json(SEEN_JSON, seen)
    print(f"{n} queued in {f}")

def status():
    rows = reg.load()
    by = {}
    for r in rows:
        by[r.get("detect_status") or "unchecked"] = by.get(r.get("detect_status") or "unchecked", 0) + 1
    ats = {}
    for r in rows:
        if r.get("ats"):
            ats[r["ats"]] = ats.get(r["ats"], 0) + 1
    jobs = read_csv(JOBS_CSV)
    seen = load_json(SEEN_JSON, {})
    st = {}
    for v in seen.values():
        st[v.get("state")] = st.get(v.get("state"), 0) + 1
    print(json.dumps({"companies": len(rows), "detect_status": by, "ats_feeds": ats, "jobs": len(jobs),
                      "jobs_open": sum(1 for j in jobs if j.get("status") != "closed"), "seen_urls": st,
                      "search_coverage": queries.coverage()}, indent=1, ensure_ascii=False))

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    today = dt.date.today().isoformat()
    s = sub.add_parser("fetch"); s.add_argument("--date", default=today)
    s.add_argument("--sources", default="ats,arbeitnow,ba,karriere"); s.add_argument("--stale-days", type=int, default=0)
    s.add_argument("--max-companies", type=int); s.add_argument("--workers", type=int, default=12)
    s.add_argument("--dry", action="store_true"); s.add_argument("--max-new", type=int, default=200)
    s.add_argument("--only", default="", help="comma-separated company names (substring match); ATS feeds only")
    s = sub.add_parser("add-url"); s.add_argument("urls", nargs="+"); s.add_argument("--date", default=today)
    s = sub.add_parser("ingest"); s.add_argument("--date", default=today)
    s = sub.add_parser("analyze"); s.add_argument("--date", default=today)
    s = sub.add_parser("import-companies"); s.add_argument("file")
    s = sub.add_parser("add-company"); s.add_argument("name"); s.add_argument("--domain", default="")
    s.add_argument("--careers", default=""); s.add_argument("--country", default="")
    s.add_argument("--ats", default=""); s.add_argument("--slug", default=""); s.add_argument("--via", default="manual")
    s = sub.add_parser("detect"); s.add_argument("--limit", type=int); s.add_argument("--workers", type=int, default=16)
    s.add_argument("--only")
    s = sub.add_parser("queries"); s.add_argument("--n", type=int, default=15)
    s = sub.add_parser("log-query"); s.add_argument("query"); s.add_argument("--found", type=int, default=0)
    s = sub.add_parser("check-active"); s.add_argument("--older-than", type=int, default=30)
    s.add_argument("--workers", type=int, default=16); s.add_argument("--limit", type=int)
    s.add_argument("--dry", action="store_true")
    sub.add_parser("status")
    a = ap.parse_args()

    if a.cmd == "fetch":
        fetch.run(a.date, tuple(a.sources.split(",")), a.stale_days, a.max_companies, a.workers, a.dry, a.max_new,
                  only=[x.strip().lower() for x in a.only.split(",") if x.strip()])
    elif a.cmd == "add-url":
        add_url(a.urls, a.date)
    elif a.cmd == "ingest":
        ingest.run(a.date)
    elif a.cmd == "analyze":
        subprocess.run([sys.executable, "analysis_gen.py", a.date], check=True)
    elif a.cmd == "import-companies":
        reg.import_file(a.file)
    elif a.cmd == "add-company":
        rows = reg.load()
        r, created = reg.add(rows, a.name, a.domain, a.careers, a.country, a.via, a.ats, a.slug)
        reg.save(rows); print(("added: " if created else "exists/updated: ") + a.name)
    elif a.cmd == "detect":
        reg.detect(a.limit, a.workers, a.only)
    elif a.cmd == "queries":
        print("\n".join(queries.next_queries(a.n)))
    elif a.cmd == "log-query":
        queries.log_query(a.query, a.found)
    elif a.cmd == "check-active":
        from pipeline import active
        active.run(a.older_than, a.workers, dry=a.dry, limit=a.limit)
    elif a.cmd == "status":
        status()

if __name__ == "__main__":
    main()
