"""One-off migration (idempotent): new job_id formula, country + status columns,
seed companies.csv and state/seen.json from the existing jobs.csv."""
import collections
from urllib.parse import urlparse
from .common import JOBS_CSV, JOB_FIELDS, SEEN_JSON, canon_url, country_of, load_json, make_job_id, read_csv, \
    save_json, write_csv
from . import companies as reg

AGGREGATORS = ("arbeitnow.com", "karriere.at", "datacareer.ch", "linkedin.", "indeed.", "stepstone.", "glassdoor.",
               "arbeitsagentur.de", "jobs.ch", "xing.com")

def run():
    jobs = read_csv(JOBS_CSV)
    ids = collections.Counter()
    for j in jobs:
        j["job_id"] = make_job_id(j["company"], j["job_title"], j["location"])
        j["country"] = j.get("country") or country_of(j["location"])
        j["status"] = j.get("status") or "open"
        ids[j["job_id"]] += 1
    dups = [k for k, v in ids.items() if v > 1]
    write_csv(JOBS_CSV, jobs, JOB_FIELDS)
    seen = load_json(SEEN_JSON, {})
    for j in jobs:
        seen.setdefault(canon_url(j["posting_url"]), {"state": "ingested", "job_id": j["job_id"],
                                                       "first": j["first_seen_date"], "last": j["last_seen_date"]})
    save_json(SEEN_JSON, seen)
    rows = reg.load()
    for j in jobs:
        host = urlparse(j["posting_url"]).netloc.lower()
        own = host and not any(a in host for a in AGGREGATORS)
        reg.add(rows, j["company"], careers_url=j["posting_url"] if own else "", country=j["country"],
                via="seed:jobs.csv")
    reg.save(rows)
    print(f"migrated {len(jobs)} jobs; duplicate ids after migration: {len(dups)}; registry: {len(rows)} companies")
    print("countries:", dict(collections.Counter(j["country"] for j in jobs)))

if __name__ == "__main__":
    run()
