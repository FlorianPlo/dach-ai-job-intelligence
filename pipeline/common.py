"""Shared helpers: HTTP, text cleanup, DACH location + relevance filters, CSV/state IO.

Stdlib only, so the pipeline runs anywhere (local, cloud agent) without installs.
"""
import csv, gzip, hashlib, html, json, os, re, time, unicodedata, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state"
INBOX = ROOT / "inbox"
JOBS_CSV = ROOT / "jobs.csv"
COMPANIES_CSV = ROOT / "companies.csv"
SEEN_JSON = STATE / "seen.json"

UA = "Mozilla/5.0 (compatible; dach-job-research/1.0; personal labour-market research)"

# ---------------------------------------------------------------- HTTP

def http(url, data=None, headers=None, timeout=20, retries=2, method=None):
    """GET/POST a URL. Returns (status, text). Never raises for HTTP errors."""
    h = {"User-Agent": UA, "Accept": "application/json, text/html, application/xml;q=0.9, */*;q=0.5",
         "Accept-Encoding": "gzip"}
    h.update(headers or {})
    body = None
    if data is not None:
        body = json.dumps(data).encode() if not isinstance(data, bytes) else data
        h.setdefault("Content-Type", "application/json")
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, data=body, headers=h, method=method)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
                return r.status, raw.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504) and attempt < retries:
                time.sleep(2 * (attempt + 1)); continue
            return e.code, ""
        except Exception:
            if attempt < retries:
                time.sleep(1 + attempt); continue
            return 0, ""
    return 0, ""


def http_json(url, **kw):
    st, txt = http(url, **kw)
    if st != 200 or not txt:
        return st, None
    try:
        return st, json.loads(txt)
    except ValueError:
        return st, None

# ---------------------------------------------------------------- text

_TAG = re.compile(r"<[^>]+>")
_BLOCK = re.compile(r"</?(p|div|li|ul|ol|br|h\d|tr|section)[^>]*>", re.I)

def html_to_text(s):
    if not s:
        return ""
    s = html.unescape(s) if "&lt;" in s else s          # some feeds double-escape HTML
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S | re.I)
    s = _BLOCK.sub("\n", s)
    s = _TAG.sub(" ", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t\xa0]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


# Boilerplate sections that cost tokens but carry no skill signal.
_BOILER = re.compile(r"^(benefits|what we offer|wir bieten|unser angebot|das bieten wir|perks|why join|"
                     r"about us|über uns|ueber uns|equal opportunit|diversity|chancengleich|"
                     r"datenschutz|privacy|how to apply|bewerbung)\b", re.I)
_KEEP = re.compile(r"^(requirements|your profile|qualifications|what you bring|you have|skills|"
                   r"anforderungen|dein profil|ihr profil|das bringst du mit|was du mitbringst|"
                   r"responsibilities|tasks|aufgaben|your role|deine aufgaben|ihre aufgaben|nice to have)\b", re.I)

def trim_description(text, limit=3500):
    """Drop boilerplate sections (benefits, about-us, EEO) and cap length.

    Keeps salary sentences even inside dropped sections, so pay info is never lost.
    """
    if not text:
        return ""
    out, skipping = [], False
    for line in text.splitlines():
        l = line.strip()
        if not l:
            continue
        short = len(l) < 60
        if short and _BOILER.match(l):
            skipping = True; continue
        if short and _KEEP.match(l):
            skipping = False
        if skipping and not re.search(r"(€|EUR|CHF|gehalt|salary|brutto|jahres|vergütung|kv\b)", l, re.I):
            continue
        out.append(l)
    t = "\n".join(out)
    return t if len(t) <= limit else t[:limit] + " …[truncated]"

# ---------------------------------------------------------------- location

COUNTRY_WORDS = {
    "Germany": ["germany", "deutschland", "(de)", ", deu "],
    "Switzerland": ["switzerland", "schweiz", "suisse", "svizzera", "(ch)", ", che "],
    "Austria": ["austria", "österreich", "oesterreich", "(at)", ", aut "],
}
CITIES = {
    "Germany": ["berlin", "munich", "münchen", "muenchen", "hamburg", "frankfurt", "cologne", "köln", "koeln",
                "stuttgart", "düsseldorf", "duesseldorf", "dortmund", "essen", "leipzig", "dresden", "hannover",
                "nuremberg", "nürnberg", "nuernberg", "bremen", "bonn", "mannheim", "karlsruhe", "heidelberg",
                "freiburg", "darmstadt", "aachen", "münster", "augsburg", "wiesbaden", "mainz", "potsdam",
                "jena", "tübingen", "tuebingen", "ulm", "regensburg", "würzburg", "wuerzburg", "erlangen",
                "ingolstadt", "wolfsburg", "braunschweig", "kiel", "lübeck", "rostock", "saarbrücken",
                "koblenz", "gilching", "garching", "walldorf", "baden-baden", "bielefeld", "paderborn",
                "göttingen", "kassel", "chemnitz", "magdeburg", "erfurt", "oberkochen", "herzogenaurach"],
    "Switzerland": ["zurich", "zürich", "zuerich", "geneva", "genève", "geneve", "genf", "basel", "bern", "lausanne",
                    "zug", "lucerne", "luzern", "winterthur", "st. gallen", "st gallen", "lugano", "fribourg",
                    "baar", "neuchâtel", "neuchatel", "schaffhausen", "aarau", "baden, ch", "rotkreuz",
                    "dübendorf", "duebendorf", "kloten", "schlieren", "thalwil", "rüschlikon", "allschwil"],
    "Austria": ["vienna", "wien", "graz", "linz", "salzburg", "innsbruck", "klagenfurt", "villach", "wels",
                "st. pölten", "st. poelten", "dornbirn", "leoben", "hagenberg", "steyr", "bregenz",
                "wiener neustadt", "krems", "eisenstadt", "hörsching", "lieboch"],
}
NON_DACH = ["london", "united kingdom", "paris", "amsterdam", "new york", "san francisco", "usa", "united states",
            "india", "bangalore", "warsaw", "poland", "madrid", "barcelona", "lisbon", "dublin", "toronto",
            "singapore", "tokyo", "milan", "stockholm", "copenhagen", "prague", "budapest", "bucharest",
            "utrecht", "rotterdam", "eindhoven", "the hague", "brussels", "lyon", "nantes", "lille", "toulouse",
            "manchester", "edinburgh", "cambridge, uk", "oxford", "france", "netherlands", "nederland",
            "belgium", "spain", "italy", "portugal", "ireland", "england", ", uk"]

def _fold(s):
    return " " + unicodedata.normalize("NFC", (s or "")).lower().replace("_", " ") + " "

def countries_in(location):
    """Return the set of DACH countries a free-text location mentions."""
    l = _fold(location)
    found = set()
    for c, words in COUNTRY_WORDS.items():
        if any(w in l for w in words):
            found.add(c)
    for c, cities in CITIES.items():
        if any(re.search(r"(?<![a-zäöü])" + re.escape(x) + r"(?![a-zäöü])", l) for x in cities):
            found.add(c)
    return found

def country_of(location):
    """Primary DACH country for a location string ('' if none). 'Zurich/London' -> Switzerland."""
    l = _fold(location)
    tail = l.strip().split(",")[-1].strip()
    for c in COUNTRY_WORDS:
        if tail == c.lower():
            return c
    cs = countries_in(location)
    if not cs:
        return ""
    # first mention wins when several (e.g. 'Munich/Vienna')
    pos = {}
    for c in cs:
        terms = COUNTRY_WORDS[c] + CITIES[c]
        idx = [l.find(t) for t in terms if t in l]
        pos[c] = min(idx) if idx else 10**6
    return min(pos, key=pos.get)

def is_dach(location, remote_ok=False):
    if countries_in(location):
        return True
    l = _fold(location)
    if remote_ok and ("remote" in l and ("europe" in l or "emea" in l or "dach" in l)):
        return True
    return " dach " in l

# ---------------------------------------------------------------- relevance

RELEVANT = re.compile(
    r"(data scien|datenwissenschaft|machine learning|maschinelles lernen|\bml\b|\bmlops\b|\bllm|"
    r"\bai\b|\bki\b|artificial intelligence|künstliche intelligenz|kuenstliche intelligenz|deep learning|"
    r"computer vision|\bnlp\b|natural language|data engineer|datenengineer|daten-engineer|analytics engineer|"
    r"research scientist|research engineer|applied scientist|genai|generative|"
    r"data platform|data architect|ml ops|reinforcement learning|perception|"
    r"forecasting|recommender|speech recognition|robot learning|ki-engineer|ki engineer|ki-entwickl|ki entwickl)", re.I)
EXCLUDE = re.compile(
    r"(sales|vertrieb|account exec|account manager|marketing|recruit|talent acqui|\bhr\b|steuerberat|"
    r"tax advis|legal|counsel|jurist|buchhalt|accountant|customer success|support agent|video editor|"
    r"content creator|copywriter|social media|office manag|assistenz|sekretär|lagerist|fahrer|driver|"
    r"pflege|nurse|einkäuf|procurement|business development|partnership|duales studium|dualer student|"
    r"dual study|ausbildung|umschulung|weiterbildung|bachelor of science|b\.sc|studienarbeit|projektarbeit|"
    r"abschlussarbeit|masterarbeit|bachelorarbeit|thesis|product manag|produktmanag|product owner|"
    r"projektleiter|project manager|projektmanag|governance|compliance|lehrkraft|dozent|trainer|teacher|"
    r"professur|professor|consultant sap|sap berater|vertriebs|key account|fp&a|engagement manager|"
    r"founder associate|venture builder|transformation lead|business consultant|strategy|strategie|"
    r"allrounder|change manag)", re.I)
# training providers / course sellers posting 'jobs'
COMPANY_EXCLUDE = re.compile(r"(alfatraining|bildungszentrum|akademie|academy|weiterbildung|bildungswerk)", re.I)
# staffing / recruiting intermediaries: kept but de-prioritised (spec prefers original postings)
STAFFING = re.compile(r"(ferchau|hays|randstad|adecco|gulp|manpower|persona[l]?(dienst|service|vermittl)|"
                      r"zeitarbeit|recruit|headhunt|search ltd|executive search|talents? gmbh|home of jobs|"
                      r"jobware|constaff|allatnet|amadeus fire|brunel|etengo|solcom|computer futures|"
                      r"michael page|robert half|experis|darwin recruitment|harvey nash)", re.I)
ENTRY = re.compile(r"(junior|graduate|absolvent|berufseinsteiger|einsteiger|einstieg|trainee|working student|"
                   r"werkstudent|praktik|intern\b|internship|thesis|abschlussarbeit|masterarbeit|bachelorarbeit|"
                   r"entry.level|new grad|doktorand|phd student)", re.I)

TECH = re.compile(r"\b(python|sql|pyspark|spark|pytorch|tensorflow|scikit|pandas|numpy|machine learning|"
                  r"maschinelles lernen|deep learning|llms?|rag|nlp|computer vision|mlops|databricks|snowflake|"
                  r"airflow|dbt|kafka|etl|elt|data pipelines?|datenpipelines?|data warehouse|data lake|"
                  r"kubernetes|docker|hugging ?face|langchain|transformers?|neural|modell(?:e|ierung)?|"
                  r"statisti\w*|forecast\w*|embeddings?|fine-?tuning|bigquery|azure ml|sagemaker|vertex|"
                  r"reinforcement learning|inference|cuda|agentic|ai agents?|ki-agenten|prompt\w*|openai|"
                  r"postgresql|n8n|automati[sz]ierung|automation|api|genai|generative|ki-modelle?|ai models?)\b", re.I)

def is_relevant_text(text, need=2):
    """Content check: at least `need` distinct data/ML terms. Catches feeds that label
    unrelated jobs with a generic occupation title (e.g. AMS 'Data Engineer' security roles)."""
    return len({m.group(1).lower() for m in TECH.finditer(text or "")}) >= need

def is_relevant_title(title):
    t = title or ""
    return bool(RELEVANT.search(t)) and not EXCLUDE.search(t)

# ---------------------------------------------------------------- normalization / ids

_GENDER = re.compile(r"\(\s*[mwfdxhai/*:|,\s-]{3,}\s*\)|\b[mwfd]\s*/\s*[mwfd]\s*/\s*[mwfdx]\b|\*innen|:innen", re.I)

def norm_title(title):
    t = _GENDER.sub(" ", title or "")
    t = re.sub(r"[^\wäöüß+#]+", " ", t.lower())
    return re.sub(r"\s+", " ", t).strip()

def norm_company(name):
    n = (name or "").lower()
    n = re.sub(r"\b(gmbh|ag|se|kg|co|inc|ltd|llc|sa|sàrl|sarl|plc|ug|mbh|group|holding|deutschland|"
               r"austria|schweiz|switzerland|germany)\b", " ", n)
    n = re.sub(r"[^\wäöüß]+", " ", n)
    return re.sub(r"\s+", " ", n).strip()

def city_of(location):
    return (location or "").split(",")[0].split("/")[0].strip().lower()

def make_job_id(company, title, location):
    """Stable id = company + normalized title + primary city.

    Distinct roles at the same company/city stay separate; the same posting seen via
    two sources (e.g. Arbeitnow and the company ATS) collapses to one row.
    """
    key = f"{norm_company(company)}|{norm_title(title)}|{city_of(location)}"
    return hashlib.sha1(key.encode()).hexdigest()[:12]

def canon_url(url):
    u = (url or "").strip()
    u = re.sub(r"[?#].*$", "", u) if "gh_jid" not in u else u
    return u.rstrip("/").lower()

# ---------------------------------------------------------------- CSV / state IO

def read_csv(path):
    p = Path(path)
    if not p.exists():
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_csv(path, rows, fields):
    tmp = Path(str(path) + ".tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})
    os.replace(tmp, path)

def load_json(path, default):
    p = Path(path)
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))

def save_json(path, obj):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(p) + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8")
    os.replace(tmp, p)

JOB_FIELDS = ["job_id", "job_title", "normalized_role", "seniority", "seniority_basis", "company", "location",
              "country", "work_type", "salary_min", "salary_max", "salary_currency", "salary_period",
              "required_skills", "nice_to_have_skills", "years_experience", "education_required",
              "language_requirements", "posting_url", "posting_date", "source", "first_seen_date",
              "last_seen_date", "status"]

COMPANY_FIELDS = ["company", "domain", "careers_url", "country", "ats", "ats_slug", "detect_status",
                  "detect_date", "last_fetched", "relevant_open", "relevant_total", "added_date", "added_via",
                  "notes"]
