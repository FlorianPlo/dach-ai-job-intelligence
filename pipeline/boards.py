"""Job-board sources with public structured access.

- Arbeitnow API (DE, JSON, full description included)
- Bundesagentur für Arbeit Jobbörse API (DE federal job board — largest DE source;
  public read key 'jobboerse-jobsuche', the one its own website uses)
- karriere.at (AT) — listing HTML -> per-posting schema.org JobPosting JSON-LD
Also: jsonld_posting(url) — generic extractor used for any careers page URL.
"""
import base64, json, re, threading, time
from urllib.parse import quote
from .common import http, http_json, html_to_text, is_relevant_title, is_dach

# ---------------------------------------------------------------- JSON-LD (generic)

def jsonld_posting(url):
    """Return (posting dict | None) from a page's schema.org JobPosting block."""
    st, h = http(url, timeout=25, headers={"Accept": "text/html"})
    if st != 200:
        return None
    for b in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', h, re.S):
        try:
            d = json.loads(b.strip())
        except ValueError:
            continue
        items = d if isinstance(d, list) else d.get("@graph", [d]) if isinstance(d, dict) else []
        for it in items:
            if isinstance(it, dict) and it.get("@type") == "JobPosting":
                return _from_jsonld(it, url)
    return None

def _from_jsonld(d, url):
    locs = d.get("jobLocation") or []
    locs = locs if isinstance(locs, list) else [locs]
    parts = []
    for l in locs:
        a = (l or {}).get("address") or {}
        if isinstance(a, dict):
            city = re.sub(r"^\d{4,5}\s+", "", a.get("addressLocality", "") or "")
            parts.append(", ".join(x for x in [city, a.get("addressCountry") if isinstance(a.get("addressCountry"), str)
                                              else (a.get("addressCountry") or {}).get("name", "")] if x))
    sal = ""
    bs = d.get("baseSalary") or {}
    if isinstance(bs, dict):
        v = bs.get("value") or {}
        if isinstance(v, dict):
            lo, hi, unit = v.get("minValue") or v.get("value"), v.get("maxValue"), v.get("unitText", "")
            if lo:
                sal = f"{lo}-{hi or ''} {bs.get('currency','')}/{unit}"
    iso = {"AT": "Austria", "DE": "Germany", "CH": "Switzerland", "LI": "Liechtenstein",
           "AUT": "Austria", "DEU": "Germany", "CHE": "Switzerland"}
    parts = [re.sub(r",\s*([A-Z]{2,3})$", lambda m: ", " + iso.get(m.group(1), m.group(1)), x) for x in parts]
    org = d.get("hiringOrganization") or {}
    remote = "TELECOMMUTE" in str(d.get("jobLocationType", "")).upper()
    return {"company": org.get("name", "") if isinstance(org, dict) else str(org), "title": d.get("title", ""),
            "location": " | ".join(p for p in parts if p), "url": url,
            "description": html_to_text(d.get("description", "")), "posted": (d.get("datePosted") or "")[:10],
            "remote": remote, "salary_text": sal, "source": ""}

# ---------------------------------------------------------------- Arbeitnow

def _arbeitnow_loc(loc):
    from .common import countries_in
    if not loc:
        return "Germany"
    from .common import NON_DACH
    if countries_in(loc) or "," in loc or any(w in loc.lower() for w in NON_DACH):
        return loc                    # Arbeitnow also lists UK/FR/NL jobs: never force ", Germany"
    return f"{loc}, Germany"

def arbeitnow(max_pages=8):
    out = []
    for page in range(1, max_pages + 1):
        st, d = http_json(f"https://www.arbeitnow.com/api/job-board-api?page={page}", timeout=40)
        if not d or not d.get("data"):
            break
        for j in d["data"]:
            out.append({"company": j.get("company_name", ""), "title": j.get("title", ""),
                        "location": _arbeitnow_loc(j.get("location", "")),
                        "url": j.get("url"), "description": html_to_text(j.get("description", "")),
                        "posted": time.strftime("%Y-%m-%d", time.gmtime(int(j.get("created_at") or 0))),
                        "remote": bool(j.get("remote")), "salary_text": "", "source": "Arbeitnow API"})
        if not (d.get("links") or {}).get("next"):
            break
    return out

# ---------------------------------------------------------------- Bundesagentur für Arbeit

BA = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service"
BA_KEY = {"X-API-Key": "jobboerse-jobsuche"}
_BA_SLOTS = threading.Semaphore(3)   # BA detail endpoint drops requests under heavier parallel load
BA_LAND = {"DEUTSCHLAND": "Germany", "SCHWEIZ": "Switzerland", "OESTERREICH": "Austria",
           "ÖSTERREICH": "Austria", "LIECHTENSTEIN": "Liechtenstein"}
BA_QUERIES = ["Data Scientist", "Machine Learning", "Data Engineer", "KI Engineer", "AI Engineer",
              "Künstliche Intelligenz", "Deep Learning", "Computer Vision", "MLOps", "LLM",
              "Werkstudent Data Science", "Werkstudent KI", "Junior Data Scientist", "Absolvent Data Science"]

def arbeitsagentur(days=31, max_pages=3, queries=None):
    out, seen = [], set()
    for q in queries or BA_QUERIES:
        for page in range(1, max_pages + 1):
            st, d = http_json(f"{BA}/pc/v6/jobs?was={quote(q)}&size=100&page={page}&veroeffentlichtseit={days}",
                              headers=BA_KEY, timeout=30)
            items = (d or {}).get("ergebnisliste") or []
            for j in items:
                ref = j.get("referenznummer") or j.get("refnr")
                if j.get("stellenangebotsart") not in (None, "ARBEIT"):      # skip AUSBILDUNG/dual-study
                    continue
                if not ref or ref in seen:
                    continue
                seen.add(ref)
                locs = j.get("stellenlokationen") or [{}]
                l = locs[0].get("adresse") or j.get("arbeitsort") or {}
                ext = j.get("externeUrl", "")
                def detail(ref=ref, ext=ext):
                    b = base64.b64encode(ref.encode()).decode()
                    with _BA_SLOTS:
                        _, dd = http_json(f"{BA}/pc/v4/jobdetails/{b}", headers=BA_KEY, timeout=30, retries=3)
                    txt = (dd or {}).get("stellenangebotsBeschreibung", "")
                    ext2 = ext or (dd or {}).get("externeUrl", "") or (dd or {}).get("allianzpartnerUrl", "")
                    if not txt and ext2:              # posting lives on the employer's site
                        p = jsonld_posting(ext2)
                        txt = (p or {}).get("description", "")
                    return txt
                out.append({"company": j.get("firma", ""), "title": j.get("stellenangebotsTitel") or j.get("titel", ""),
                            "location": f"{l.get('ort','').split(',')[0]}, "
                                        f"{BA_LAND.get(l.get('land', ''), 'Germany')}", "url":
                            f"https://www.arbeitsagentur.de/jobsuche/jobdetail/{ref}",
                            "description": "", "posted": j.get("datumErsteVeroeffentlichung") or
                            j.get("aktuelleVeroeffentlichungsdatum", ""), "remote": bool(j.get("homeofficemoeglich")),
                            "salary_text": "", "source": "Bundesagentur für Arbeit API", "_detail": detail,
                            "external_url": j.get("externeUrl", "")})
            if len(items) < 100:
                break
    return out

# ---------------------------------------------------------------- karriere.at

KARRIERE_QUERIES = ["data-scientist", "machine-learning", "machine-learning-engineer", "ai-engineer",
                    "data-engineer", "kuenstliche-intelligenz", "junior-data-scientist", "data-science-praktikum",
                    "werkstudent-data-science", "mlops", "computer-vision"]

def karriere(max_pages=3, queries=None):
    """Listing pages give ids + titles; detail (JSON-LD) is fetched lazily for relevant ones."""
    out, seen = [], set()
    card = re.compile(r'href="(https://www\.karriere\.at/jobs/(\d+))"[^>]*>\s*([^<]{3,160})<', re.S)
    for q in queries or KARRIERE_QUERIES:
        for page in range(1, max_pages + 1):
            st, h = http(f"https://www.karriere.at/jobs/{q}" + (f"?page={page}" if page > 1 else ""),
                         timeout=25, headers={"Accept": "text/html"})
            if st != 200:
                break
            hits = card.findall(h)
            new = 0
            for url, jid, title in hits:
                if jid in seen:
                    continue
                seen.add(jid); new += 1
                def detail(url=url):
                    p = jsonld_posting(url)
                    return p or {}
                out.append({"company": "", "title": html_to_text(title), "location": "Austria", "url": url,
                            "description": "", "posted": "", "remote": False, "salary_text": "",
                            "source": "karriere.at", "_detail_full": detail})
            if not new:
                break
    return out
