"""Adapters for public applicant-tracking-system (ATS) feeds.

Each adapter: list_jobs(slug, company) -> list of posting dicts:
    {company, title, location, url, description, posted, remote, salary_text, source, _detail}
`_detail` (optional) is a zero-arg callable that fetches the full description lazily,
so we only pay for detail requests on postings that pass the relevance filter.

No login, no scraping of blocked pages: these are the endpoints companies publish
for their own career sites.
"""
import re, xml.etree.ElementTree as ET
from urllib.parse import quote
from .common import http, http_json, html_to_text

SEARCH_TERMS = ["data", "machine learning", "AI", "KI", "ML", "scientist", "LLM"]

def _p(company, title, location, url, description="", posted="", remote=False, salary_text="", source="", detail=None):
    d = {"company": company, "title": (title or "").strip(), "location": (location or "").strip(), "url": url,
         "description": description or "", "posted": (posted or "")[:10], "remote": bool(remote),
         "salary_text": salary_text or "", "source": source}
    if detail:
        d["_detail"] = detail
    return d

# ---------------------------------------------------------------- Greenhouse

def greenhouse(slug, company):
    st, d = http_json(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true", timeout=40)
    if not d:
        return None
    out = []
    for j in d.get("jobs", []):
        loc = (j.get("location") or {}).get("name", "")
        offices = ", ".join(o.get("name", "") for o in j.get("offices", []) if o.get("name"))
        out.append(_p(j.get("company_name") or company, j.get("title"), loc + (" | " + offices if offices else ""),
                      j.get("absolute_url"), html_to_text(j.get("content", "")),
                      j.get("first_published") or j.get("updated_at", ""), "remote" in loc.lower(),
                      source=f"Greenhouse ({slug})"))
    return out

# ---------------------------------------------------------------- Lever (US + EU hosts)

def lever(slug, company):
    d = None
    for host in ("api.lever.co", "api.eu.lever.co"):
        st, d = http_json(f"https://{host}/v0/postings/{slug}?mode=json", timeout=40)
        if isinstance(d, list):
            break
    if not isinstance(d, list):
        return None
    out = []
    for j in d:
        c = j.get("categories") or {}
        locs = c.get("allLocations") or [c.get("location", "")]
        desc = j.get("descriptionPlain", "") + "\n" + "\n".join(
            f"{l.get('text','')}\n{html_to_text(l.get('content',''))}" for l in j.get("lists", []))
        out.append(_p(company, j.get("text"), ", ".join(x for x in locs if x), j.get("hostedUrl"),
                      desc + "\n" + (j.get("additionalPlain") or ""), "", j.get("workplaceType") == "remote",
                      source=f"Lever ({slug})"))
    return out

# ---------------------------------------------------------------- Ashby

def ashby(slug, company):
    st, d = http_json(f"https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true", timeout=40)
    if not d or "jobs" not in d:
        return None
    out = []
    for j in d["jobs"]:
        if j.get("isListed") is False:
            continue
        locs = [j.get("location", "")] + [s.get("location", "") for s in j.get("secondaryLocations") or []]
        addr = ((j.get("address") or {}).get("postalAddress") or {}).get("addressCountry", "")
        comp = (j.get("compensation") or {}).get("scrapeableCompensationSalarySummary") or ""
        out.append(_p(company, j.get("title"), ", ".join(x for x in locs if x) + (f", {addr}" if addr else ""),
                      j.get("jobUrl"), j.get("descriptionPlain", ""), j.get("publishedAt", ""),
                      bool(j.get("isRemote")), comp, source=f"Ashby ({slug})"))
    return out

# ---------------------------------------------------------------- Personio (XML, .de or .com)

def personio(slug, company):
    for tld in ("de", "com"):
        st, txt = http(f"https://{slug}.jobs.personio.{tld}/xml?language=en", timeout=40)
        if st == 200 and "<workzag-jobs" in txt:
            break
    else:
        return None
    try:
        root = ET.fromstring(txt)
    except ET.ParseError:
        return None
    out = []
    for pos in root.findall("position"):
        g = lambda k: (pos.findtext(k) or "").strip()
        offices = [g("office")] + [o.text or "" for o in pos.findall("additionalOffices/office")]
        desc = "\n".join(f"{(d.findtext('name') or '').strip()}\n{html_to_text(d.findtext('value') or '')}"
                         for d in pos.findall("jobDescriptions/jobDescription"))
        out.append(_p(company, g("name"), ", ".join(o for o in offices if o),
                      f"https://{slug}.jobs.personio.{tld}/job/{g('id')}", desc, g("createdAt"),
                      source=f"Personio ({slug})"))
    return out

# ---------------------------------------------------------------- Recruitee

def recruitee(slug, company):
    st, d = http_json(f"https://{slug}.recruitee.com/api/offers/", timeout=40)
    if not d or "offers" not in d:
        return None
    out = []
    for j in d["offers"]:
        sal = j.get("salary") or {}
        sal_t = f"{sal.get('min')}-{sal.get('max')} {sal.get('currency')}/{sal.get('period')}" if sal.get("min") else ""
        loc = ", ".join(x for x in [j.get("city"), j.get("country")] if x) or j.get("location", "")
        out.append(_p(j.get("company_name") or company, j.get("title"), loc, j.get("careers_url"),
                      html_to_text((j.get("description") or "") + "\n" + (j.get("requirements") or "")),
                      j.get("published_at", ""), bool(j.get("remote")), sal_t, source=f"Recruitee ({slug})"))
    return out

# ---------------------------------------------------------------- SmartRecruiters (lazy details)

def smartrecruiters(slug, company):
    out, seen = [], set()
    for term in SEARCH_TERMS:
        st, d = http_json(f"https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=100&q={quote(term)}",
                          timeout=30)
        if d is None:
            if not out and term == SEARCH_TERMS[0]:
                return None
            continue
        for j in d.get("content", []):
            if j["id"] in seen:
                continue
            seen.add(j["id"])
            loc = j.get("location") or {}
            loc_s = ", ".join(x for x in [loc.get("city"), (loc.get("country") or "").upper()] if x)
            ref = j.get("ref")
            def detail(ref=ref):
                _, dd = http_json(ref, timeout=30)
                if not dd:
                    return ""
                secs = (dd.get("jobAd") or {}).get("sections") or {}
                return "\n".join(html_to_text((secs.get(k) or {}).get("text", ""))
                                 for k in ("jobDescription", "qualifications", "additionalInformation"))
            out.append(_p((j.get("company") or {}).get("name") or company, j.get("name"), loc_s,
                          f"https://jobs.smartrecruiters.com/{slug}/{j['id']}", "", j.get("releasedDate", ""),
                          bool(loc.get("remote")), source=f"SmartRecruiters ({slug})", detail=detail))
    return out

# ---------------------------------------------------------------- Workable

def workable(slug, company):
    st, d = http_json(f"https://apply.workable.com/api/v1/widget/accounts/{slug}?details=true", timeout=40)
    if not d or "jobs" not in d:
        return None
    out = []
    for j in d["jobs"]:
        loc = ", ".join(x for x in [j.get("city"), j.get("country")] if x)
        out.append(_p(d.get("name") or company, j.get("title"), loc, j.get("url") or j.get("shortlink"),
                      html_to_text(j.get("description", "")), j.get("published_on", ""),
                      bool(j.get("telecommuting")), source=f"Workable ({slug})"))
    return out

# ---------------------------------------------------------------- Workday (slug = tenant|wdN|site)

def workday(slug, company):
    try:
        tenant, wd, site = slug.split("|")
    except ValueError:
        return None
    base = f"https://{tenant}.{wd}.myworkdayjobs.com"
    api = f"{base}/wday/cxs/{tenant}/{site}"
    out, seen, ok = [], set(), False
    for term in ["data", "machine learning", "AI", "KI"]:
        for offset in range(0, 200, 20):
            st, d = http_json(f"{api}/jobs", data={"appliedFacets": {}, "limit": 20, "offset": offset,
                                                   "searchText": term}, timeout=30)
            if not d:
                break
            ok = True
            posts = d.get("jobPostings", [])
            for j in posts:
                path = j.get("externalPath")
                if not path or path in seen:
                    continue
                seen.add(path)
                def detail(path=path):
                    _, dd = http_json(f"{api}{path}", timeout=30)
                    info = (dd or {}).get("jobPostingInfo") or {}
                    return html_to_text(info.get("jobDescription", ""))
                out.append(_p(company, j.get("title"), j.get("locationsText", ""), f"{base}/{site}{path}", "",
                              "", False, source=f"Workday ({tenant})", detail=detail))
            if len(posts) < 20:
                break
    return out if ok else None


ADAPTERS = {"greenhouse": greenhouse, "lever": lever, "ashby": ashby, "personio": personio,
            "recruitee": recruitee, "smartrecruiters": smartrecruiters, "workable": workable, "workday": workday}

# URL patterns that reveal a company's ATS (used by detect.py on careers pages).
EMBED_PATTERNS = [
    ("greenhouse", re.compile(r"(?:boards|job-boards)(?:\.eu)?\.greenhouse\.io/(?:embed/job_board\?for=)?([\w-]+)", re.I)),
    ("greenhouse", re.compile(r"boards-api\.greenhouse\.io/v1/boards/([\w-]+)", re.I)),
    ("lever", re.compile(r"jobs\.(?:eu\.)?lever\.co/([\w.-]+)", re.I)),
    ("ashby", re.compile(r"jobs\.ashbyhq\.com/([\w.%-]+)", re.I)),
    ("personio", re.compile(r"([\w-]+)\.jobs\.personio\.(?:de|com)", re.I)),
    ("recruitee", re.compile(r"([\w-]+)\.recruitee\.com", re.I)),
    ("smartrecruiters", re.compile(r"(?:careers|jobs)\.smartrecruiters\.com/([\w-]+)", re.I)),
    ("workable", re.compile(r"apply\.workable\.com/([\w-]+)", re.I)),
    ("workday", re.compile(r"([\w-]+)\.(wd\d+)\.myworkdayjobs\.com/(?:[a-z]{2}-[A-Z]{2}/)?([\w-]+)", re.I)),
]
IGNORE_SLUGS = {"embed", "api", "v1", "js", "static", "assets", "www", "jobs", "careers", "en", "de", "job_app"}
