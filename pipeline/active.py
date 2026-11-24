"""Check whether stored postings are still online -> jobs.csv `status` (2nd column).

Order of evidence per posting (first conclusive answer wins):
  1. ATS API (exact): Greenhouse, Lever, Ashby, SmartRecruiters, Personio, Recruitee,
     Workable, Bundesagentur für Arbeit
  2. Generic page check: 404/410 -> closed; redirect that drops the job id (e.g. to a search
     page) -> closed; "no longer available"-type text -> closed; JSON-LD validThrough in the
     past -> closed; JSON-LD JobPosting or the job title on the page -> open
  3. Anything else (403, bot wall, timeout, ambiguous page) -> unknown. Never guessed.

status values: open | closed | unknown (checked, inconclusive) | unverified (never checked)
"""
import base64, datetime as dt, json, re, threading, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlsplit, parse_qs
from .common import UA, JOBS_CSV, JOB_FIELDS, http, http_json, norm_title, read_csv, write_csv

# ---------------------------------------------------------------- feed caches (one call per board)
_cache, _lock = {}, threading.Lock()

def _cached(key, fn):
    with _lock:
        if key in _cache:
            return _cache[key]
    v = fn()
    with _lock:
        _cache[key] = v
    return v

def _ashby_ids(slug):
    _, d = http_json(f"https://api.ashbyhq.com/posting-api/job-board/{slug}", timeout=40)
    return None if not d or "jobs" not in d else {j["id"] for j in d["jobs"]}

def _personio_ids(slug, tld):
    st, txt = http(f"https://{slug}.jobs.personio.{tld}/xml", timeout=40)
    return None if st != 200 or "<workzag-jobs" not in txt else set(re.findall(r"<id>(\d+)</id>", txt))

def _recruitee_slugs(slug):
    _, d = http_json(f"https://{slug}.recruitee.com/api/offers/", timeout=40)
    return None if not d or "offers" not in d else {o.get("slug") for o in d["offers"]}

# ---------------------------------------------------------------- exact API checks

def _api_check(url):
    """Return 'open' / 'closed' / None (not an ATS we can check exactly)."""
    p = urlsplit(url); host = p.netloc.lower(); path = p.path
    q = parse_qs(p.query)
    # Greenhouse: boards / job-boards(.eu).greenhouse.io/<slug>/jobs/<id>
    m = re.search(r"greenhouse\.io/([\w-]+)/jobs/(\d+)", host + path)
    if m:
        st, _ = http(f"https://boards-api.greenhouse.io/v1/boards/{m.group(1)}/jobs/{m.group(2)}", timeout=20)
        return {200: "open", 404: "closed"}.get(st)
    # Lever (US/EU): jobs(.eu).lever.co/<slug>/<uuid>
    m = re.search(r"jobs\.(eu\.)?lever\.co/([\w.-]+)/([0-9a-f-]{36})", host + path)
    if m:
        api = "api.eu.lever.co" if m.group(1) else "api.lever.co"
        st, _ = http(f"https://{api}/v0/postings/{m.group(2)}/{m.group(3)}", timeout=20)
        return {200: "open", 404: "closed"}.get(st)
    # Ashby: jobs.ashbyhq.com/<slug>/<uuid>
    m = re.search(r"jobs\.ashbyhq\.com/([^/]+)/([0-9a-f-]{36})", host + path)
    if m:
        ids = _cached(("ashby", m.group(1).lower()), lambda: _ashby_ids(m.group(1)))
        return None if ids is None else ("open" if m.group(2) in ids else "closed")
    # SmartRecruiters: jobs.smartrecruiters.com/<slug>/<id>[-title]
    m = re.search(r"smartrecruiters\.com/([\w-]+)/(\d{6,})", host + path)
    if m:
        st, d = http_json(f"https://api.smartrecruiters.com/v1/companies/{m.group(1)}/postings/{m.group(2)}", timeout=20)
        if st == 404:
            return "closed"
        if d:
            return "open" if d.get("active", True) else "closed"
        return None
    # Personio: <slug>.jobs.personio.(de|com)/job/<id>
    m = re.search(r"([\w-]+)\.jobs\.personio\.(de|com)/job/(\d+)", host + path)
    if m:
        ids = _cached(("personio", m.group(1)), lambda: _personio_ids(m.group(1), m.group(2)))
        return None if ids is None else ("open" if m.group(3) in ids else "closed")
    # Recruitee: <slug>.recruitee.com/o/<offer-slug>
    m = re.search(r"([\w-]+)\.recruitee\.com/o/([\w-]+)", host + path)
    if m:
        slugs = _cached(("recruitee", m.group(1)), lambda: _recruitee_slugs(m.group(1)))
        return None if slugs is None else ("open" if m.group(2) in slugs else "closed")
    # Workable: apply.workable.com/<slug>/j/<shortcode>
    m = re.search(r"apply\.workable\.com/([\w-]+)/j/(\w+)", host + path)
    if m:
        st, _ = http(f"https://apply.workable.com/api/v2/accounts/{m.group(1)}/jobs/{m.group(2)}", timeout=20)
        return {200: "open", 404: "closed"}.get(st)
    # Workday: <tenant>.wdN.myworkdayjobs.com/[locale/]<site>/job/<...>
    m = re.search(r"([\w-]+)\.(wd\d+)\.myworkdayjobs\.com/(?:[a-z]{2}-[A-Z]{2}/)?([\w-]+)(/job/.+)$", host + path)
    if m:
        tenant, wd, site, jpath = m.groups()
        st, d = http_json(f"https://{tenant}.{wd}.myworkdayjobs.com/wday/cxs/{tenant}/{site}{jpath}", timeout=20)
        if d and d.get("jobPostingInfo"):
            return "open"
        return "closed" if st in (404, 410) else None
    # Bundesagentur für Arbeit
    m = re.search(r"arbeitsagentur\.de/jobsuche/jobdetail/([\w-]+)", host + path)
    if m:
        b = base64.b64encode(m.group(1).encode()).decode()
        st, d = http_json(f"https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobdetails/{b}",
                          headers={"X-API-Key": "jobboerse-jobsuche"}, timeout=20)
        if d and d.get("stellenangebotsTitel"):
            return "open"
        if st == 404 or (d and "NICHT_GEFUNDEN" in json.dumps(d)):
            return "closed"
        return None
    return None

# ---------------------------------------------------------------- generic page check

CLOSED_TXT = re.compile(
    r"(no longer (?:available|accepting applications|active|open)|this (?:job|position|role) (?:is|has been) "
    r"(?:closed|filled|removed)|position has been filled|job (?:posting )?(?:has )?expired|job not found|"
    r"vacancy (?:is )?closed|nicht mehr (?:verfügbar|aktiv|online|besetzbar)|bereits besetzt|"
    r"stelle (?:ist )?(?:leider )?(?:nicht mehr|bereits)|ausschreibung (?:ist )?(?:beendet|abgelaufen)|"
    r"stellenanzeige (?:ist )?(?:abgelaufen|nicht mehr)|offre (?:n'est plus|expirée)|"
    r"annonce (?:n'est plus|a expiré))", re.I)
BLOCKED_TXT = re.compile(r"(captcha|enable js|access denied|cloudflare|are you a robot|attention required)", re.I)

def _fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*;q=0.8",
                                               "Accept-Language": "en,de;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.geturl(), r.read(600_000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, url, ""
    except Exception:
        return 0, url, ""

def _id_tokens(url):
    """Digits/uuid-ish tokens that identify the job in a URL (to detect 'redirected away')."""
    p = urlsplit(url)
    toks = re.findall(r"[0-9a-f]{8}-[0-9a-f-]{27,}|\d{5,}", (p.path + "?" + p.query).lower())
    return set(toks)

def _looks_like_posting(url):
    """A URL that identifies ONE job (id/uuid, or a descriptive multi-word slug) — not a search/landing page."""
    p = urlsplit(url); path = p.path.lower()
    if "karriere.at" in p.netloc and not re.search(r"/jobs/\d+", path):
        return False
    if _id_tokens(url) or re.search(r"(job|stelle|vacanc|position|offer|o)[^/]*/[^/]*[a-z]+-[a-z]+-[a-z]+", path):
        return True
    last = path.rstrip("/").rsplit("/", 1)[-1]
    return last.count("-") >= 3

def _segments(u):
    return [x for x in urlsplit(u).path.split("/") if x and not re.fullmatch(r"[a-z]{2}([-_][a-z]{2})?", x, re.I)]

def _generic_check(url, title):
    st, final, html = _fetch(url)
    if st in (404, 410):
        return "closed", f"http {st}"
    if st != 200:
        return "unknown", f"http {st}" if st else "unreachable"
    if not _looks_like_posting(url):
        return "unknown", "stored URL is a search/landing page"
    ids = _id_tokens(url)
    if ids and not (ids & _id_tokens(final)) and final.rstrip("/") != url.rstrip("/"):
        return "closed", "redirected away from posting"
    if not ids and final.rstrip("/") != url.rstrip("/"):
        s0, s1 = _segments(url), _segments(final)
        if len(s1) < len(s0) or (s0 and s1 and s0[-1].lower() != s1[-1].lower()):
            return "closed", "redirected to generic page"
    if BLOCKED_TXT.search(html[:20000]) and len(html) < 20000:
        return "unknown", "bot wall"
    for b in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', html, re.S):
        try:
            d = json.loads(b.strip())
        except ValueError:
            continue
        items = d if isinstance(d, list) else d.get("@graph", [d]) if isinstance(d, dict) else []
        for it in items:
            if isinstance(it, dict) and it.get("@type") == "JobPosting":
                vt = (it.get("validThrough") or "")[:10]
                if vt and vt < dt.date.today().isoformat():
                    return "closed", f"validThrough {vt}"
                return "open", "JSON-LD JobPosting"
    text = re.sub(r"<[^>]+>", " ", html)
    if CLOSED_TXT.search(text):
        return "closed", "closed notice on page"
    # title must appear in the page <title> or <h1> (not just anywhere, e.g. a "similar jobs" list)
    heads = " ".join(a + " " + b for a, b in re.findall(r"<title[^>]*>(.*?)</title>|<h1[^>]*>(.*?)</h1>", html, re.S | re.I))
    heads = re.sub(r"<[^>]+>", " ", heads).lower()
    words = [w for w in norm_title(title).split() if len(w) > 3][:4]
    if words and sum(w in heads for w in words) >= max(1, len(words) - 1):
        return "open", "title in page heading"
    return "unknown", "ambiguous page"

_GH_BY_COMPANY = None

def _registry_greenhouse(row):
    """Company careers sites that embed Greenhouse (e.g. helsing.ai/jobs/<id>): check via the
    company's known Greenhouse slug from companies.csv."""
    global _GH_BY_COMPANY
    if _GH_BY_COMPANY is None:
        from .companies import load
        from .common import norm_company
        _GH_BY_COMPANY = {norm_company(r["company"]): r["ats_slug"] for r in load() if r.get("ats") == "greenhouse"}
    from .common import norm_company
    slug = _GH_BY_COMPANY.get(norm_company(row["company"]))
    m = re.search(r"(?:gh_jid=|/)(\d{7,})", row["posting_url"])
    if not (slug and m):
        return None
    st, _ = http(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs/{m.group(1)}", timeout=20)
    return {200: "open", 404: "closed"}.get(st)

def check_one(row):
    url = row["posting_url"]
    try:
        api = _api_check(url) or _registry_greenhouse(row)
        if api:
            return row, api, "ATS/API"
        return (row,) + _generic_check(url, row["job_title"])
    except Exception as e:  # one bad posting must not abort the run
        return row, "unknown", f"error {type(e).__name__}"

def run(older_than_days=30, workers=16, today=None, dry=False, limit=None):
    today = today or dt.date.today().isoformat()
    cutoff = (dt.date.fromisoformat(today) - dt.timedelta(days=older_than_days)).isoformat()
    jobs = read_csv(JOBS_CSV)
    todo = [j for j in jobs if (j.get("last_seen_date") or "") < cutoff and j.get("status") != "closed"]
    todo = todo[:limit] if limit else todo
    print(f"checking {len(todo)} postings last seen before {cutoff} ({workers} parallel)…", flush=True)
    res, why = {}, {}
    with ThreadPoolExecutor(workers) as ex:
        for i, (row, status, reason) in enumerate(ex.map(check_one, todo), 1):
            res[row["job_id"]] = status; why[row["job_id"]] = reason
            if i % 100 == 0:
                print(f"  {i}/{len(todo)}", flush=True)
    for j in jobs:
        s = res.get(j["job_id"])
        if s:
            j["status"] = s
            j["active_checked_date"] = today
            if s == "open":
                j["last_seen_date"] = today
    if not dry:
        write_csv(JOBS_CSV, jobs, JOB_FIELDS)
    from collections import Counter
    summary = {"checked": len(todo), "result": dict(Counter(res.values())),
               "reasons": dict(Counter(why.values()).most_common(12)),
               "status_all_jobs": dict(Counter(j.get("status") or "?" for j in jobs))}
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    return summary, res, why
