"""Company registry (companies.csv): import, add, and ATS detection.

Detection order per company (stops at first hit):
  1. careers page / homepage HTML -> look for embedded ATS links (most reliable)
  2. slug guessing against public ATS feeds; a guess is only accepted if the feed
     has >=1 posting located in DACH (filters out same-named foreign companies)
Results are cached in companies.csv (detect_status/detect_date), so each company is
probed once; 'none' results are retried after RETRY_DAYS.
"""
import re, sys, datetime as dt
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urljoin
from .common import (COMPANIES_CSV, COMPANY_FIELDS, http, http_json, is_dach, norm_company, read_csv, write_csv)
from . import ats

RETRY_DAYS = 90
TODAY = dt.date.today().isoformat()

def load():
    return read_csv(COMPANIES_CSV)

def save(rows):
    rows.sort(key=lambda r: r["company"].lower())
    write_csv(COMPANIES_CSV, rows, COMPANY_FIELDS)

def _index(rows):
    return {norm_company(r["company"]): r for r in rows}

def _domain(s):
    s = (s or "").strip()
    if not s:
        return ""
    if "://" not in s:
        s = "https://" + s
    h = urlparse(s).netloc.lower()
    return h[4:] if h.startswith("www.") else h

def add(rows, company, domain="", careers_url="", country="", via="manual", ats_name="", slug="", notes=""):
    """Insert if new (by normalized name); fill blanks if existing. Returns (row, created)."""
    idx = _index(rows)
    key = norm_company(company)
    if not key:
        return None, False
    r = idx.get(key)
    if r:
        for k, v in (("domain", _domain(domain)), ("careers_url", careers_url), ("country", country),
                     ("ats", ats_name), ("ats_slug", slug)):
            if v and not r.get(k):
                r[k] = v
        if ats_name and slug and r.get("detect_status") in ("", "none"):
            r["detect_status"], r["detect_date"] = "found", TODAY
        return r, False
    r = {f: "" for f in COMPANY_FIELDS}
    r.update(company=company.strip(), domain=_domain(domain), careers_url=careers_url.strip(), country=country,
             ats=ats_name, ats_slug=slug, added_date=TODAY, added_via=via, notes=notes,
             detect_status="found" if (ats_name and slug) else "", detect_date=TODAY if ats_name else "")
    rows.append(r)
    return r, True

NAME_COLS = ["company", "name", "firma", "unternehmen", "company_name", "organisation", "organization", "employer"]
DOMAIN_COLS = ["domain", "website", "url", "homepage", "web", "site"]
CAREER_COLS = ["careers_url", "careers", "career_url", "karriere", "jobs_url", "jobs"]
COUNTRY_COLS = ["country", "land", "staat", "country_code"]

def import_file(path):
    """Import a CSV/TSV/TXT list. Header names are matched loosely; a header-less
    one-column file is treated as company names."""
    import csv
    text = open(path, encoding="utf-8-sig").read()
    rows = load()
    before = len(rows)
    first = text.splitlines()[0] if text else ""
    delim = "\t" if "\t" in first else (";" if first.count(";") > first.count(",") else ",")
    reader = list(csv.reader(text.splitlines(), delimiter=delim))
    header = [h.strip().lower() for h in reader[0]] if reader else []
    def col(cands):
        for c in cands:
            if c in header:
                return header.index(c)
        return None
    ni = col(NAME_COLS)
    body = reader[1:] if ni is not None else reader
    ni = 0 if ni is None else ni
    di, ci, ki = col(DOMAIN_COLS), col(CAREER_COLS), col(COUNTRY_COLS)
    g = lambda row, i: row[i].strip() if i is not None and i < len(row) else ""
    for row in body:
        if not row or not g(row, ni):
            continue
        add(rows, g(row, ni), g(row, di), g(row, ci), g(row, ki), via=f"import:{path.split('/')[-1]}")
    save(rows)
    print(f"imported: {len(rows) - before} new companies (registry now {len(rows)})")

# ---------------------------------------------------------------- detection

def _scan_html(txt):
    txt = re.sub(r"\\u002f|\\/|%2f", "/", txt, flags=re.I)   # JSON-/URL-escaped slashes
    for name, pat in ats.EMBED_PATTERNS:
        for m in pat.finditer(txt):
            if name == "workday":
                return name, f"{m.group(1)}|{m.group(2)}|{m.group(3)}"
            slug = m.group(1).strip(".").lower() if name != "ashby" else m.group(1).strip(".")
            if slug and slug not in ats.IGNORE_SLUGS:
                return name, slug
    return None

_CAREER_LINK = re.compile(r'href="([^"]+)"[^>]*>[^<]{0,40}(karriere|career|jobs|stellen|join us|work with us)', re.I)

def _from_pages(r):
    urls = []
    if r.get("careers_url"):
        urls.append(r["careers_url"])
    d = r.get("domain")
    if d:
        urls += [f"https://{d}/careers", f"https://{d}/karriere", f"https://{d}/jobs", f"https://{d}"]
    for u in urls:
        st, txt = http(u, timeout=12, retries=0)
        if st != 200 or not txt:
            continue
        hit = _scan_html(txt)
        if hit:
            return hit, u
        if u.endswith(d or "@@"):        # homepage: follow one careers link
            m = _CAREER_LINK.search(txt)
            if m:
                cu = urljoin(u + "/", m.group(1))
                st2, txt2 = http(cu, timeout=12, retries=0)
                if st2 == 200:
                    hit = _scan_html(txt2)
                    if hit:
                        return hit, cu
    return None, ""

def _slug_candidates(name, domain):
    base = norm_company(name)
    toks = base.split()
    c = []
    if toks:
        c += ["".join(toks), "-".join(toks)]
        if len(toks) == 1:                          # first-word-only guesses ('anton', 'julius') hit other firms
            c.append(toks[0])
    if domain:
        c.append(domain.split(".")[0])
    seen, out = set(), []
    for s in c:
        s = re.sub(r"[^a-z0-9-]", "", s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss"))
        if len(s) >= 2 and s not in seen:
            seen.add(s); out.append(s)
    return out[:3]

GUESSABLE = ["greenhouse", "ashby", "lever", "personio", "recruitee", "workable", "smartrecruiters"]

def _from_guess(r):
    for slug in _slug_candidates(r["company"], r.get("domain")):
        for name in GUESSABLE:
            jobs = ats.ADAPTERS[name](slug, r["company"])
            if jobs and any(is_dach(j["location"], remote_ok=False) for j in jobs):
                return name, slug
    return None

def detect_one(r):
    try:
        hit, _ = _from_pages(r)
        if hit:
            return r, hit, "found"
        hit = _from_guess(r)
        if hit:
            return r, hit, "guessed"
        return r, None, "none"
    except Exception as e:  # one bad company must not abort the batch
        return r, None, f"error:{type(e).__name__}"

def needs_detect(r):
    st = r.get("detect_status", "")
    if st in ("found", "guessed", "manual"):
        return False
    if st == "" or st.startswith("error"):
        return True
    try:
        return (dt.date.today() - dt.date.fromisoformat(r["detect_date"])).days >= RETRY_DAYS
    except ValueError:
        return True

def detect(limit=None, workers=16, only=None):
    rows = load()
    todo = [r for r in rows if needs_detect(r) and (not only or only.lower() in r["company"].lower())]
    todo = todo[:limit] if limit else todo
    print(f"detecting ATS for {len(todo)} companies ({workers} parallel)…", flush=True)
    done = found = 0
    with ThreadPoolExecutor(workers) as ex:
        for fut in as_completed([ex.submit(detect_one, r) for r in todo]):
            r, hit, status = fut.result()
            r["detect_status"], r["detect_date"] = status, TODAY
            if hit:
                r["ats"], r["ats_slug"] = hit
                found += 1
            done += 1
            if done % 100 == 0:
                save(rows); print(f"  {done}/{len(todo)} checked, {found} with a feed", flush=True)
    save(rows)
    print(f"done: {done} checked, {found} with a usable feed")
