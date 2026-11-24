"""Rotating web-search query plan, so each run searches *further* instead of repeating.

The matrix = role terms × places (× entry-level words) × search sites. `next_queries(n)`
returns never-tried queries first, then the least-recently-used ones weighted by past yield.
The agent logs each query's yield with `log_query`, stored in state/search_log.json.

Aggregators (Indeed, LinkedIn, StepStone, XING, jobs.ch, Glassdoor) are used ONLY via
search-result snippets to learn *company + title*; the agent then finds the original
posting (company ATS / careers page). Their pages are never fetched.
"""
import datetime as dt, hashlib, itertools, random
from .common import STATE, load_json, save_json

LOG = STATE / "search_log.json"

ROLES = ["Machine Learning Engineer", "Data Scientist", "AI Engineer", "Data Engineer", "MLOps Engineer",
         "Research Scientist AI", "Applied Scientist", "Computer Vision Engineer", "NLP Engineer", "LLM Engineer",
         "KI Entwickler", "Datenwissenschaftler", "Analytics Engineer"]
ENTRY = ["Junior", "Werkstudent", "Graduate", "Praktikum", "Absolvent", "Trainee", "PhD"]
PLACES = ["Zürich", "Basel", "Bern", "Lausanne", "Genf", "Zug", "Wien", "Graz", "Linz", "Salzburg", "Innsbruck",
          "Berlin", "München", "Hamburg", "Frankfurt", "Köln", "Stuttgart", "Karlsruhe", "Heidelberg", "Darmstadt",
          "Dresden", "Leipzig", "Aachen", "Tübingen", "Nürnberg", "Düsseldorf", "Remote DACH"]
CH = {"Zürich", "Basel", "Bern", "Lausanne", "Genf", "Zug"}
AT = {"Wien", "Graz", "Linz", "Salzburg", "Innsbruck"}
SITES_BY = {
    "CH": ["", "site:ch.indeed.com", "site:linkedin.com/jobs", "site:jobs.ch", "site:greenhouse.io",
           "site:jobs.lever.co", "site:jobs.ashbyhq.com", "site:jobs.smartrecruiters.com"],
    "AT": ["", "site:at.indeed.com", "site:linkedin.com/jobs", "site:stepstone.at", "site:jobs.personio.de",
           "site:greenhouse.io"],
    "DE": ["", "site:de.indeed.com", "site:linkedin.com/jobs", "site:stepstone.de", "site:xing.com/jobs",
           "site:jobs.personio.de", "site:greenhouse.io", "site:jobs.ashbyhq.com"],
}
SITES = ["", "site:indeed.com", "site:de.indeed.com", "site:ch.indeed.com", "site:at.indeed.com",
         "site:linkedin.com/jobs", "site:stepstone.de", "site:jobs.ch", "site:xing.com/jobs",
         "site:greenhouse.io", "site:jobs.lever.co", "site:jobs.ashbyhq.com", "site:jobs.personio.de"]

def all_queries():
    qs = [f"{r} {p}" for r, p in itertools.product(ROLES, PLACES)]
    qs += [f"{e} {r} {p}" for e, r, p in itertools.product(ENTRY, ROLES[:6], PLACES[:20])]
    rnd = random.Random(42)                      # deterministic site assignment per query
    def region(q):
        return "CH" if any(c in q for c in CH) else "AT" if any(c in q for c in AT) else "DE"
    return [f"{q} {rnd.choice(SITES_BY[region(q)])}".strip() for q in qs]

def next_queries(n=15, entry_share=0.4):
    log = load_json(LOG, {})
    qs = all_queries()
    def score(q):
        e = log.get(q)
        if not e:                               # never tried first, in a stable shuffled order
            return (0, hashlib.md5(q.encode()).hexdigest())
        return (1, e["last"] + f"{-e.get('yield', 0):06d}")
    entry = sorted([q for q in qs if any(w in q for w in ENTRY)], key=score)
    other = sorted([q for q in qs if not any(w in q for w in ENTRY)], key=score)
    k = int(n * entry_share)
    return entry[:k] + other[:n - k]

def log_query(q, found=0, date=None):
    log = load_json(LOG, {})
    e = log.get(q, {"runs": 0, "yield": 0})
    e["runs"] += 1
    e["yield"] = e.get("yield", 0) + int(found)
    e["last"] = date or dt.date.today().isoformat()
    log[q] = e
    save_json(LOG, log)

def coverage():
    log = load_json(LOG, {})
    qs = all_queries()
    return {"total_queries": len(qs), "tried": sum(1 for q in qs if q in log),
            "productive": sum(1 for q in qs if log.get(q, {}).get("yield", 0) > 0)}
