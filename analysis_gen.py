#!/usr/bin/env python3
"""Regenerate skills_by_level.md, salary_benchmarks.md and the daily report from jobs.csv.
Usage: python3 analysis_gen.py <RUN_DATE>  (e.g. 2026-06-23)
Trend deltas compare current full dataset vs the snapshot of rows first seen BEFORE RUN_DATE.
"""
import csv, sys
from collections import Counter, defaultdict

RUN = sys.argv[1]
_raw_rows = list(csv.DictReader(open("jobs.csv")))

# --- defensive read (additive, non-breaking) ---------------------------------
# csv.DictReader yields None for missing trailing columns on a ragged row, and a
# stray un-headered column lands under the None key. Normalize every expected field
# to a string so downstream .split()/index lookups never crash on a single bad row
# (Quality rule: "one bad posting must not abort the run"). Well-formed rows are
# unaffected — this only fills missing/None values with "".
_FIELDS = ("job_id","job_title","normalized_role","seniority","seniority_basis",
           "company","location","work_type","salary_min","salary_max",
           "salary_currency","salary_period","required_skills","nice_to_have_skills",
           "years_experience","education_required","language_requirements",
           "posting_url","posting_date","source","first_seen_date","last_seen_date")
rows = []
_skipped = 0
for _r in _raw_rows:
    # A row with no job_id and no title is structurally broken; skip it loudly.
    if not (_r.get("job_id") or _r.get("job_title")):
        _skipped += 1
        continue
    rows.append({f: (_r.get(f) or "") for f in _FIELDS})
if _skipped:
    sys.stderr.write(f"[analysis_gen] WARNING: skipped {_skipped} malformed row(s) "
                     f"missing job_id and job_title.\n")

N = len(rows)
order = ["Intern","Junior","Mid","Senior","Lead/Principal"]

# ---------------- in-memory skill canonicalization (backlog #1) ----------------
# jobs.csv is NEVER modified by this script. The alias map below is applied at READ
# time only, so that frequency counts don't split across spelling variants
# (e.g. "Microsoft Azure" and "Azure"). All matching is on the FULL skill token
# (exact, case-insensitive), never substring — so compound tokens that are
# genuinely distinct stay distinct: "LLM APIs", "LLM Fine-Tuning", "Azure OpenAI",
# "Torch Distributor", "torch.distributed", "GraphRAG", "PySpark", "SparkML" are
# all left untouched. To merge a new variant, add a lowercased key below.
_SKILL_ALIASES = {
    # --- cloud ---
    "microsoft azure": "Azure",
    "k8s": "Kubernetes",
    # --- libraries / frameworks ---
    "sklearn": "scikit-learn",
    "torch": "PyTorch",            # standalone only; "PyTorch", "torch.distributed" unaffected
    "tensorflow": "TensorFlow",    # lowercase variant -> canonical case
    # --- Hugging Face family ---
    "hf": "Hugging Face",
    "huggingface": "Hugging Face",
    "hugging face transformers": "Hugging Face",
    # --- LLM umbrella (collapse singular/long form to the plural umbrella) ---
    # NOTE: only the bare tokens collapse; "LLM APIs", "LLM Fine-Tuning", "LLMOps",
    # "LLM Evals" etc. are distinct concepts and are intentionally NOT mapped here.
    "llm": "LLMs",
    "large language models": "LLMs",
    # --- generative AI (pick one canonical form) ---
    "genai": "Generative AI",
    "generative ai": "Generative AI",
    # --- case collapses observed live in jobs.csv (same concept, different casing) ---
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "vector databases": "Vector Databases",   # case split: "vector databases"(5)/"Vector Databases"(6)
    # --- LLM tooling / orchestration libs (case safety nets; bare tokens only) ---
    "langchain": "LangChain",
    "llamaindex": "LlamaIndex",
    # --- model providers / families (future-proofing; bare full tokens only).
    # NOTE: compounds like "Azure OpenAI", "OpenAI Codex", "OpenAI API" stay distinct —
    # only the bare provider token collapses. "openai api" folded into OpenAI deliberately. ---
    "openai": "OpenAI",
    "openai api": "OpenAI",
    "anthropic": "Anthropic",
    "vllm": "vLLM",
    "mistral": "Mistral",
    "llama": "Llama",                          # bare "llama" only; "LlamaIndex"/"LlamaParse" unaffected
    # --- cloud / BI casing collapses ---
    "google cloud": "GCP",                     # same product as GCP
    "google cloud platform": "GCP",
    "powerbi": "Power BI",                     # "PowerBI"(2)/"Power BI"(14)
    "amazon web services": "AWS",
    # --- spacing / hyphen / vendor-prefix splits the case-fold can't catch (2026-06-27).
    # These differ by MORE than case (punctuation/spacing/vendor prefix), so _CASE_MAP
    # leaves them split. All keys are full lowercased tokens; compounds like "Spark
    # Streaming", "SparkML", "AWS Bedrock", "GCP Vertex AI" are byte-distinct once
    # lowercased and stay separate (verified). Vendor-prefix folds mirror the existing
    # "Microsoft Azure"->Azure / "Google Cloud"->GCP decisions. ---
    "apache airflow": "Airflow",            # "Apache Airflow"(8) + "Airflow"(18)
    "apache spark": "Spark",                # "Apache Spark"(6) + "Spark"(34); PySpark/SparkML/SparkSQL/Spark Streaming stay distinct
    "apache kafka": "Kafka",                # "Apache Kafka"(2) + "Kafka"(13); same Apache vendor-prefix fold as Spark/Airflow (2026-06-28)
    "amazon sagemaker": "SageMaker",        # vendor-prefix fold; "SageMaker"(4)
    "aws sagemaker": "SageMaker",
    "datamesh": "Data Mesh",                # "DataMesh"(1) -> "Data Mesh"(3)
    "datavault": "Data Vault",              # "DataVault"(1) -> "Data Vault"(1)
    "ms-sql": "MS SQL",                     # "MS-SQL"(1) -> "MS SQL"(1)
    "infrastructure-as-code": "Infrastructure as Code",  # hyphen split of same concept
    # Time-series: fold both "forecasting" and "analysis" phrasings to a single
    # canonical "Time Series Forecasting" (2026-06-29). The raw data carried 5 split
    # spellings (Time Series Analysis / Time series analysis / time series analysis /
    # Time Series Forecasting / time series forecasting) for what postings use
    # interchangeably (e.g. Siemens). Picking one canonical stops the count splitting.
    "time-series forecasting": "Time Series Forecasting",
    "time series forecasting": "Time Series Forecasting",
    "time-series analysis": "Time Series Forecasting",
    "time series analysis": "Time Series Forecasting",
    "restful api": "REST API",              # spelling variant of REST API
    "restful apis": "REST APIs",
}
# ---------------- generic case-fold canonicalization (additive, 2026-06-25) ----------------
# The explicit _SKILL_ALIASES map above only collapses the handful of case splits someone
# remembered to hand-add (machine learning, deep learning, ...). But the live data carries
# ~48 case-only splits of the SAME skill — e.g. "pandas"/"Pandas", "MLflow"/"MLFlow",
# "Data Pipelines"/"data pipelines", "Computer Vision"/"computer vision". These are the
# identical concept differing ONLY by letter case, so counting them separately is pure noise.
# This pass derives, for every lowercased skill token seen in the dataset, the single casing
# that appears MOST OFTEN, and folds all other casings of that token to it. It can never merge
# genuinely distinct skills: two tokens collapse only if they are byte-identical once lowercased
# (so "Azure OpenAI" vs "Azure" or "RAG" vs "GraphRAG" are untouched — they differ by more than
# case). Explicit _SKILL_ALIASES still wins (applied first), so curated decisions are preserved.
# Ties (same frequency) resolve to the lexicographically-larger string, which favours Title/Upper
# case over lowercase deterministically. jobs.csv is NOT modified — read-time only.
def _build_case_map():
    raw = Counter()
    for _r in rows:
        for _field in ("required_skills", "nice_to_have_skills"):
            for _s in _r[_field].split(";"):
                _s = _s.strip()
                if not _s:
                    continue
                # apply explicit alias first so the case-vote is taken over canonical forms
                _s = _SKILL_ALIASES.get(_s.lower(), _s)
                raw[_s] += 1
    best = {}
    for tok, n in raw.items():
        low = tok.lower()
        prevbest = best.get(low)
        if prevbest is None or (n, tok) > (raw[prevbest], prevbest):
            best[low] = tok
    return best

def canon(s):
    """Map a single skill token to its canonical spelling.
    Order: (1) explicit _SKILL_ALIASES (curated), then (2) generic case-fold to the
    most-frequent casing of that exact token in the dataset. Unknown tokens with a single
    casing are returned unchanged."""
    s = s.strip()
    s = _SKILL_ALIASES.get(s.lower(), s)
    return _CASE_MAP.get(s.lower(), s)

_CASE_MAP = _build_case_map()

def sk(r): return [canon(s) for s in r["required_skills"].split(";") if s.strip()]
def nth(r): return [canon(s) for s in r["nice_to_have_skills"].split(";") if s.strip()]

# ---------------- location → country resolution (additive, backlog #6, 2026-06-25) ----------
# country() takes the last comma-segment of `location`. Rows stored as "City, Country" resolve
# correctly. But a few rows carry a SLASHED multi-city string with NO comma (e.g. "Munich/Berlin",
# "Zurich/London", "Heidelberg/Berlin"); for those the whole string was returned as the "country",
# polluting the country mix. Rather than guess (skip-if-unsure), we use a small curated map of
# UNAMBIGUOUS DACH cities. It is applied ONLY when the location has no comma and contains a "/".
# Any slashed string whose first recognised city is in the map resolves to that city's country;
# anything unrecognised falls through to the exact prior behaviour (returns the raw last segment),
# so this is purely additive and reversible. jobs.csv is untouched.
_CITY_COUNTRY = {
    # Germany
    "munich": "Germany", "münchen": "Germany", "berlin": "Germany", "hamburg": "Germany",
    "cologne": "Germany", "köln": "Germany", "frankfurt": "Germany", "stuttgart": "Germany",
    "heidelberg": "Germany", "karlsruhe": "Germany", "düsseldorf": "Germany", "leipzig": "Germany",
    "dresden": "Germany", "garching": "Germany", "ludwigsburg": "Germany", "gilching": "Germany",
    # Switzerland
    "zurich": "Switzerland", "zürich": "Switzerland", "geneva": "Switzerland",
    "basel": "Switzerland", "bern": "Switzerland", "lausanne": "Switzerland", "lugano": "Switzerland",
    "zug": "Switzerland", "lucerne": "Switzerland", "winterthur": "Switzerland",
    # Austria
    "vienna": "Austria", "wien": "Austria", "graz": "Austria", "linz": "Austria",
    "salzburg": "Austria", "innsbruck": "Austria", "klagenfurt": "Austria",
}
# DACH country names (lowercased) used as a guard for the parenthetical strip below.
_DACH_COUNTRIES = {"germany", "switzerland", "austria"}
def country(r):
    loc = r["location"]
    if "," not in loc and "/" in loc:
        for part in loc.split("/"):
            hit = _CITY_COUNTRY.get(part.strip().lower())
            if hit:
                return hit
    last = loc.split(",")[-1].strip()
    # Parenthetical-suffix cleanup (additive, 2026-06-26): a few rows store the country
    # with a trailing work-mode parenthetical and no comma, e.g. "Germany (Remote)", which
    # leaked into the country mix as its own bucket ({'Germany':156,'Germany (Remote)':1}).
    # Strip a trailing "(...)" ONLY when the remainder is an exact DACH country name; any
    # other case (e.g. "Berlin (Remote)" still carries its comma → "Germany"; an unknown
    # remainder) falls through to the exact prior behaviour. Never guesses a non-DACH country.
    if last.endswith(")") and "(" in last:
        stripped = last[: last.rindex("(")].strip()
        if stripped.lower() in _DACH_COUNTRIES:
            return stripped
    return last

prev = [r for r in rows if r["first_seen_date"] < RUN]
new_today = [r for r in rows if r["first_seen_date"] == RUN]
Np = len(prev)

def freq(rs):
    c = Counter()
    for r in rs:
        for s in sk(r): c[s]+=1
    return c
cur_f, prev_f = freq(rows), freq(prev)

# ---------------- skills_by_level.md ----------------
L=[]
L.append("# Skills by Level — DACH Data/ML/AI Roles")
L.append(f"\n_Generated {RUN} from the full dataset of **{N} jobs** ({len(new_today)} new this run)._")
L.append(f"\nCountry mix: {dict(Counter(country(r) for r in rows))} · "
         f"Role mix: {dict(Counter(r['normalized_role'] for r in rows))} · "
         f"Seniority mix: {dict(Counter(r['seniority'] for r in rows))}")

# trends
L.append("\n## 0. Trend vs previous run")
if Np==0:
    L.append("\n_No previous snapshot — this is the first run._")
else:
    def share(c,n): return (100*c/n) if n else 0
    # Min-count threshold (backlog #5): on a small dataset a single job appearing/
    # disappearing produces large %-share swings that are pure noise. Only surface a
    # skill in the rising/falling tables if it is requested in at least MIN_TREND_COUNT
    # postings in either the previous or current snapshot. New/disappeared skills are
    # still reported separately below, so nothing is hidden — this only de-noises the
    # ranked Δpp tables. Threshold scales gently with dataset size.
    MIN_TREND_COUNT = max(2, round(N/40))
    deltas=[]
    for s in set(list(cur_f)+list(prev_f)):
        if max(cur_f.get(s,0), prev_f.get(s,0)) < MIN_TREND_COUNT: continue
        d = share(cur_f.get(s,0),N) - share(prev_f.get(s,0),Np)
        deltas.append((s,d,prev_f.get(s,0),cur_f.get(s,0)))
    rising=[d for d in sorted(deltas,key=lambda x:-x[1]) if d[1]>0][:8]
    falling=[d for d in sorted(deltas,key=lambda x:x[1]) if d[1]<0][:8]
    new_skills=[s for s in cur_f if s not in prev_f]
    gone_skills=[s for s in prev_f if s not in cur_f]
    L.append(f"\nDataset grew {Np} → {N} jobs. Trend tables exclude skills below "
             f"**{MIN_TREND_COUNT} postings** (noise floor). **Rising share** (Δ percentage points of postings):")
    L.append("\n| Skill | Prev | Now | Δpp |")
    L.append("|---|---|---|---|")
    for s,d,pc,cc in rising:
        L.append(f"| {s} | {pc} | {cc} | +{d:.0f} |")
    if new_skills:
        L.append(f"\n**Newly appearing skills this run:** {', '.join(sorted(new_skills)[:20])}")
    # falling / disappeared
    L.append("\n### Falling / disappeared skills")
    if falling:
        L.append("\n**Falling share** (Δ percentage points of postings):")
        L.append("\n| Skill | Prev | Now | Δpp |")
        L.append("|---|---|---|---|")
        for s,d,pc,cc in falling:
            L.append(f"| {s} | {pc} | {cc} | {d:.0f} |")
    else:
        L.append("\n_No skill lost share vs the previous snapshot._")
    if gone_skills:
        L.append(f"\n**Disappeared this run** (present before, absent now): {', '.join(sorted(gone_skills)[:20])}")

L.append("\n## 1. Most requested skills overall")
L.append("\n| Skill | Jobs | % of postings |")
L.append("|---|---|---|")
for s,c in cur_f.most_common(20):
    L.append(f"| {s} | {c} | {round(100*c/N)}% |")

sen_sk=defaultdict(Counter); sen_n=Counter()
for r in rows:
    sen_n[r["seniority"]]+=1
    for s in sk(r): sen_sk[r["seniority"]][s]+=1
L.append("\n## 2. Skills by seniority level")
for lv in order:
    if sen_n[lv]==0: continue
    n=sen_n[lv]
    L.append(f"\n### {lv} (n={n})")
    L.append("\n| Skill | Count | % |")
    L.append("|---|---|---|")
    for s,c in sen_sk[lv].most_common(15):
        L.append(f"| {s} | {c} | {round(100*c/n)}% |")

rs_sk=defaultdict(Counter); rs_n=Counter()
for r in rows:
    key=(r["normalized_role"],r["seniority"]); rs_n[key]+=1
    for s in sk(r): rs_sk[key][s]+=1
L.append("\n## 3. Skills by role × seniority")
for (role,lv),n in sorted(rs_n.items(), key=lambda x:(x[0][0],order.index(x[0][1]))):
    top=", ".join(f"{s} ({c})" for s,c in rs_sk[(role,lv)].most_common(8))
    L.append(f"\n- **{role} — {lv}** (n={n}): {top}")

# distinguishing senior+lead vs lower
high=Counter(); nh=0; low=Counter(); nl=0
for r in rows:
    if r["seniority"] in ("Senior","Lead/Principal"):
        nh+=1
        for s in sk(r): high[s]+=1
    elif r["seniority"] in ("Intern","Junior","Mid"):
        nl+=1
        for s in sk(r): low[s]+=1
dist=[]
for s in set(list(high)+list(low)):
    sp=100*high.get(s,0)/nh if nh else 0; lp=100*low.get(s,0)/nl if nl else 0
    if sp-lp>0 and high.get(s,0)>=2: dist.append((s,round(sp),round(lp),sp-lp))
dist.sort(key=lambda x:-x[3])
L.append("\n## 4. What gets added as you go up (Senior+Lead vs Intern/Junior/Mid)")
L.append(f"\nSkills more requested at Senior/Lead level (n={nh}) than at lower levels (n={nl}), ranked by gap:")
L.append("\n| Skill | Senior+Lead % | Lower % | Gap (pp) |")
L.append("|---|---|---|---|")
for s,sp,lp,d in dist[:15]:
    L.append(f"| {s} | {sp}% | {lp}% | +{d:.0f} |")
L.append("\n**Read:** Seniority adds **distributed data/ML infrastructure** (Spark, Delta Lake, Databricks, Kubernetes, Terraform), "
         "**MLOps/DataOps**, and **architecture ownership**. Lead/Principal postings layer **team leadership** on top. "
         "Entry levels center on applied-LLM tooling (ChatGPT/Claude/Gemini, prompt engineering, RAG) with little infra expectation.")
open("skills_by_level.md","w").write("\n".join(L))

# ---------------- salary_benchmarks.md ----------------
sal=[r for r in rows if r["salary_min"] or r["salary_max"]]
S=[]
S.append("# Salary Benchmarks — DACH Data/ML/AI Roles")
S.append(f"\n_Generated {RUN}. Only postings with explicitly stated salary — **{len(sal)} of {N}** disclosed pay. Nothing imputed._")
S.append("\n> ⚠️ Small sample; most cells are n=1–2. Austrian monthly figures are typically paid 14×/year.")
# --- CHF→EUR pinned rate (backlog #3, 2026-06-29) ----------------------------------
# Switzerland now discloses salary (Anthropic, Novartis, comparis.ch, CERN, BLP, PEAX,
# Ergon). To pool CH pay with DE/AT for the cross-country median we convert CHF→EUR at a
# FIXED, documented rate so runs stay reproducible (no live FX lookup). Re-check quarterly.
CHF_TO_EUR = 1.05   # 1 CHF = 1.05 EUR (pinned; see LEARNINGS.md backlog #3)
def to_eur(amount, currency):
    """Convert an already-annualised amount to EUR-equivalent using the pinned rate.
    EUR passes through unchanged; CHF is scaled; any other currency returns None so it is
    excluded from the EUR-equivalent pool rather than silently mis-counted."""
    if amount is None: return None
    if currency=="EUR": return amount
    if currency=="CHF": return amount*CHF_TO_EUR
    return None
# group yearly EUR by role x seniority for a rough median
def annual(r):
    try:
        lo=float(r["salary_min"]) if r["salary_min"] else None
        hi=float(r["salary_max"]) if r["salary_max"] else None
    except: return None
    vals=[v for v in (lo,hi) if v is not None]
    if not vals: return None
    mid=sum(vals)/len(vals)
    p=r["salary_period"]
    if p=="month":
        # AT convention: Austrian salaries are paid 14×/year (13th + 14th salary).
        # Annualise AT EUR monthly pay ×14; everything else ×12 (conservative).
        if r["salary_currency"]=="EUR" and country(r).endswith("Austria"):
            mid*=14
        else:
            mid*=12
    elif p=="hour": mid*=40*52   # assume 40h/week × 52 weeks
    return mid
S.append("\n## Disclosed salaries")
S.append(f"\n_CHF amounts are also shown as an EUR-equivalent (~EUR col) at the pinned rate **1 CHF = {CHF_TO_EUR} EUR** for cross-country comparison; the original currency/values are preserved._")
S.append("\n| Role | Seniority | Country | Company | Min | Max | Cur | Period | ~Annualised | ~Annualised (EUR-eq) |")
S.append("|---|---|---|---|---|---|---|---|---|---|")
for r in sorted(sal, key=lambda r:(r["normalized_role"],order.index(r["seniority"]) if r["seniority"] in order else 99)):
    a=annual(r); astr=f"~{a/1000:.0f}k" if a else "–"
    aeur=to_eur(a, r["salary_currency"]); eurstr=f"~{aeur/1000:.0f}k EUR" if aeur is not None else "–"
    S.append(f"| {r['normalized_role']} | {r['seniority']} | {country(r)} | {r['company']} | {r['salary_min'] or '–'} | {r['salary_max'] or '–'} | {r['salary_currency']} | {r['salary_period']} | {astr} | {eurstr} |")
# medians by role
S.append(f"\n## Rough annualised median by role (EUR-equivalent, all seniorities pooled)")
S.append(f"\n_Pools EUR rows plus CHF rows converted at **1 CHF = {CHF_TO_EUR} EUR** (pinned). All figures EUR-equivalent._")
byrole=defaultdict(list)
for r in sal:
    a=to_eur(annual(r), r["salary_currency"])
    if a is not None: byrole[r["normalized_role"]].append(a)
S.append("\n| Role | n | Median ~annual | Range |")
S.append("|---|---|---|---|")
import statistics
for role,vals in sorted(byrole.items()):
    S.append(f"| {role} | {len(vals)} | ~{statistics.median(vals)/1000:.0f}k | {min(vals)/1000:.0f}k–{max(vals)/1000:.0f}k |")
S.append(f"\n**Confidence: LOW.** Switzerland now discloses some salaries (converted at the pinned 1 CHF = {CHF_TO_EUR} EUR rate); samples remain small. Treat as directional only.")
open("salary_benchmarks.md","w").write("\n".join(S))

# ---------------- daily report ----------------
R=[]
R.append(f"# Daily Report — {RUN}")
R.append(f"\n## Summary")
R.append(f"- **New jobs added this run:** {len(new_today)}")
R.append(f"- **Total in database:** {N} (was {Np})")
R.append("\n## New this run — breakdown")
# Empty-run guard (additive, 2026-06-28): when a run adds no jobs (new=0, e.g. RUN date
# with no matching first_seen_date rows), the breakdown lines rendered as bare labels with
# nothing after them and "Notable new postings" was a dangling header. Emit an explicit note
# instead so a zero-new report is self-explanatory. Behaviour with new>0 is unchanged.
if not new_today:
    R.append("\n_No new jobs were added in this run (database unchanged). "
             "If this is unexpected, check that the discovery step ran and that new rows "
             "carry `first_seen_date = " + RUN + "`._")
else:
    R.append("\n**By country:** " + ", ".join(f"{k} {v}" for k,v in Counter(country(r) for r in new_today).most_common()))
    R.append("\n**By role:** " + ", ".join(f"{k} {v}" for k,v in Counter(r['normalized_role'] for r in new_today).most_common()))
    R.append("\n**By seniority:** " + ", ".join(f"{k} {v}" for k,v in Counter(r['seniority'] for r in new_today).most_common()))
    R.append("\n## Notable new postings")
    for r in new_today[:6]:
        sal_s = f" — {r['salary_min']}–{r['salary_max'] or ''} {r['salary_currency']}/{r['salary_period']}" if r['salary_min'] else ""
        R.append(f"- **{r['company']}** ({r['location']}) — {r['job_title']} [{r['seniority']}]{sal_s}")
open(f"reports/{RUN}.md","w").write("\n".join(R))
print(f"Regenerated skills_by_level.md, salary_benchmarks.md, reports/{RUN}.md  (N={N}, new={len(new_today)})")
