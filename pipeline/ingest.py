"""Merge LLM extractions (inbox/<date>/batch_NN.out.jsonl) into jobs.csv.

Each output line is one JSON object for one input posting, keyed by `url` (copy it from
the input). Either the extraction fields, or {"url": ..., "reject": "<reason>"} for postings
that turn out not to be technical AI/data roles. Validation, skill canonicalization,
job_id, country and dedupe all happen here in code.
"""
import datetime as dt, json, re
from .common import (INBOX, JOBS_CSV, JOB_FIELDS, SEEN_JSON, canon_url, country_of, load_json, make_job_id,
                     read_csv, save_json, write_csv)
from .skills import canon_list

ROLES = ["Data Scientist", "ML Engineer", "AI Engineer", "Data Engineer", "AI Researcher", "Other"]
LEVELS = ["Intern", "Junior", "Mid", "Senior", "Lead/Principal"]
WORK = ["Onsite", "Hybrid", "Remote"]
PERIODS = ["year", "month", "hour"]

def _pick(v, allowed, default=""):
    v = (v or "").strip()
    for a in allowed:
        if v.lower() == a.lower():
            return a
    return default

def _num(v):
    if v in (None, ""):
        return ""
    s = re.sub(r"[^\d.]", "", str(v).replace("'", "").replace(",", ""))
    try:
        f = float(s)
        return str(int(f)) if f == int(f) else str(f)
    except ValueError:
        return ""

def run(date=None):
    today = date or dt.date.today().isoformat()
    d = INBOX / today
    inputs = {}
    for f in sorted(d.glob("batch_*.jsonl")):
        if f.name.endswith(".out.jsonl"):
            continue
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip():
                p = json.loads(line); inputs[canon_url(p["url"])] = p
    jobs = read_csv(JOBS_CSV)
    ids = {j["job_id"] for j in jobs}
    seen = load_json(SEEN_JSON, {})
    added, rejected, dup, problems, missing = 0, 0, 0, [], set(inputs)
    for f in sorted(d.glob("batch_*.out.jsonl")):
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                x = json.loads(line)
            except ValueError:
                problems.append(f"{f.name}:{n} invalid JSON"); continue
            cu = canon_url(x.get("url") or x.get("posting_url") or "")
            src = inputs.get(cu)
            if not src:
                problems.append(f"{f.name}:{n} url not in inbox: {cu[:80]}"); continue
            missing.discard(cu)
            if x.get("reject"):
                seen[cu] = {**seen.get(cu, {}), "state": "rejected", "why": str(x["reject"])[:120], "last": today}
                rejected += 1; continue
            company = x.get("company") or src["company"]
            title = x.get("job_title") or src["title"]
            location = x.get("location") or src["location"]
            jid = make_job_id(company, title, location)
            if jid in ids:
                dup += 1; seen[cu] = {**seen.get(cu, {}), "state": "ingested", "job_id": jid}; continue
            role = _pick(x.get("normalized_role"), ROLES, "Other")
            level = _pick(x.get("seniority"), LEVELS)
            if not level:
                problems.append(f"{f.name}:{n} bad seniority {x.get('seniority')!r} -> Mid")
                level = "Mid"
            sal_min, sal_max = _num(x.get("salary_min")), _num(x.get("salary_max"))
            row = {
                "job_id": jid, "job_title": title, "normalized_role": role, "seniority": level,
                "seniority_basis": (x.get("seniority_basis") or "")[:300], "company": company,
                "location": location, "country": country_of(location) or src.get("country", ""),
                "work_type": _pick(x.get("work_type"), WORK, "Onsite"),
                "salary_min": sal_min, "salary_max": sal_max,
                "salary_currency": (x.get("salary_currency") or "").upper()[:3] if (sal_min or sal_max) else "",
                "salary_period": _pick(x.get("salary_period"), PERIODS) if (sal_min or sal_max) else "",
                "required_skills": ";".join(canon_list(x.get("required_skills"))),
                "nice_to_have_skills": ";".join(canon_list(x.get("nice_to_have_skills"))),
                "years_experience": str(x.get("years_experience") or ""),
                "education_required": x.get("education_required") or "",
                "language_requirements": x.get("language_requirements") or "",
                "posting_url": src["url"], "posting_date": (x.get("posting_date") or src.get("posted") or today)[:10],
                "source": src["source"], "first_seen_date": today, "last_seen_date": today, "status": "open",
            }
            if not row["required_skills"]:
                problems.append(f"{f.name}:{n} no skills for {title[:50]}")
            jobs.append(row); ids.add(jid); added += 1
            seen[cu] = {**seen.get(cu, {}), "state": "ingested", "job_id": jid, "last": today}
    # re-canonicalize the whole DB so alias-map improvements also fix older rows
    for j in jobs:
        for k in ("required_skills", "nice_to_have_skills"):
            j[k] = ";".join(canon_list(j.get(k, "").split(";")))
    from .active import sync_active
    sync_active(jobs)
    write_csv(JOBS_CSV, jobs, JOB_FIELDS)
    save_json(SEEN_JSON, seen)
    res = {"added": added, "rejected": rejected, "duplicates": dup, "not_extracted": len(missing),
           "total_jobs": len(jobs), "problems": problems[:30]}
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return res
