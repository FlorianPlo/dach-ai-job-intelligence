#!/usr/bin/env python3
"""Regenerate skills_by_level.md, salary_benchmarks.md and the daily report from jobs.csv.
Usage: python3 analysis_gen.py <RUN_DATE>  (e.g. 2026-06-23)
Trend deltas compare current full dataset vs the snapshot of rows first seen BEFORE RUN_DATE.
"""
import csv, sys
from collections import Counter, defaultdict

RUN = sys.argv[1]
rows = list(csv.DictReader(open("jobs.csv")))
N = len(rows)
order = ["Intern","Junior","Mid","Senior","Lead/Principal"]
def sk(r): return [s for s in r["required_skills"].split(";") if s]
def country(r): return r["location"].split(",")[-1].strip()

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
    deltas=[]
    for s in set(list(cur_f)+list(prev_f)):
        d = share(cur_f.get(s,0),N) - share(prev_f.get(s,0),Np)
        deltas.append((s,d,prev_f.get(s,0),cur_f.get(s,0)))
    rising=[d for d in sorted(deltas,key=lambda x:-x[1]) if d[1]>0][:8]
    falling=[d for d in sorted(deltas,key=lambda x:x[1]) if d[1]<0][:8]
    new_skills=[s for s in cur_f if s not in prev_f]
    gone_skills=[s for s in prev_f if s not in cur_f]
    L.append(f"\nDataset grew {Np} → {N} jobs. **Rising share** (Δ percentage points of postings):")
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
    if p=="month": mid*=12
    elif p=="hour": mid*=40*52   # assume 40h/week × 52 weeks
    return mid
S.append("\n## Disclosed salaries")
S.append("\n| Role | Seniority | Country | Company | Min | Max | Cur | Period | ~Annualised |")
S.append("|---|---|---|---|---|---|---|---|---|")
for r in sorted(sal, key=lambda r:(r["normalized_role"],order.index(r["seniority"]) if r["seniority"] in order else 99)):
    a=annual(r); astr=f"~{a/1000:.0f}k" if a else "–"
    S.append(f"| {r['normalized_role']} | {r['seniority']} | {country(r)} | {r['company']} | {r['salary_min'] or '–'} | {r['salary_max'] or '–'} | {r['salary_currency']} | {r['salary_period']} | {astr} |")
# medians by role
S.append("\n## Rough annualised median by role (EUR-equivalent, all seniorities pooled)")
byrole=defaultdict(list)
for r in sal:
    a=annual(r)
    if a and r["salary_currency"]=="EUR": byrole[r["normalized_role"]].append(a)
S.append("\n| Role | n | Median ~annual | Range |")
S.append("|---|---|---|---|")
import statistics
for role,vals in sorted(byrole.items()):
    S.append(f"| {role} | {len(vals)} | ~{statistics.median(vals)/1000:.0f}k | {min(vals)/1000:.0f}k–{max(vals)/1000:.0f}k |")
S.append("\n**Confidence: LOW.** Switzerland still discloses no salaries. Treat as directional only.")
open("salary_benchmarks.md","w").write("\n".join(S))

# ---------------- daily report ----------------
R=[]
R.append(f"# Daily Report — {RUN}")
R.append(f"\n## Summary")
R.append(f"- **New jobs added this run:** {len(new_today)}")
R.append(f"- **Total in database:** {N} (was {Np})")
R.append("\n## New this run — breakdown")
R.append("\n**By country:** " + ", ".join(f"{k} {v}" for k,v in Counter(country(r) for r in new_today).most_common()))
R.append("\n**By role:** " + ", ".join(f"{k} {v}" for k,v in Counter(r['normalized_role'] for r in new_today).most_common()))
R.append("\n**By seniority:** " + ", ".join(f"{k} {v}" for k,v in Counter(r['seniority'] for r in new_today).most_common()))
R.append("\n## Notable new postings")
for r in new_today[:6]:
    sal_s = f" — {r['salary_min']}–{r['salary_max'] or ''} {r['salary_currency']}/{r['salary_period']}" if r['salary_min'] else ""
    R.append(f"- **{r['company']}** ({r['location']}) — {r['job_title']} [{r['seniority']}]{sal_s}")
open(f"reports/{RUN}.md","w").write("\n".join(R))
print(f"Regenerated skills_by_level.md, salary_benchmarks.md, reports/{RUN}.md  (N={N}, new={len(new_today)})")
