# DACH Data/ML/AI Job Intelligence Agent

## Role
Job-market intelligence agent for **Data Science / ML Engineer / AI Engineer / Data Engineer /
AI Researcher** roles in **Switzerland, Germany, Austria**. Priorities: (1) **skills-by-level
analysis**, (2) searchable deduplicated job database, (3) salary benchmarking.

## Run mode
**On demand or monthly** (not daily). A run = one full cycle below. State persists in the repo
files; never start from scratch unless they are missing.

**Model:** run the orchestration on **Sonnet**; extraction runs on **Haiku** via the
`job-extractor` subagent. Opus is not needed for this workflow.

**Token principle:** Python does all fetching, filtering, deduping and bookkeeping (zero tokens).
The model only (a) reads *new* postings once, trimmed, in batches, and (b) does web search for
what the structured sources miss. Never WebFetch a page that `jobs.py` can fetch.

## The cycle

```bash
D=$(date +%F)
#                                            1. web-search discovery (below) -> jobs.py add-company / add-url
python3 jobs.py detect                     #    find feeds for newly registered companies
python3 jobs.py fetch --date $D            # 2. structured sources -> inbox/$D/batch_NN.jsonl
#                                            3. extraction: one job-extractor subagent per batch file
python3 jobs.py ingest --date $D           # 4. validate + canonicalize + dedupe -> jobs.csv
python3 jobs.py check-active               #    re-check postings not seen in a feed for 30+ days -> is_active
python3 jobs.py analyze --date $D          # 5. regenerate skills_by_level.md, salary_benchmarks.md, open_jobs.md, reports/$D.md
```

### 1. Fetch (automated, free)
`jobs.py fetch` pulls: every company in `companies.csv` that has a known ATS feed (Greenhouse,
Lever, Ashby, Personio, Recruitee, SmartRecruiters, Workable, Workday), the **Arbeitnow API**,
the **Bundesagentur für Arbeit API** (largest DE source, also lists some CH/AT jobs), and
**karriere.at** (AT, via schema.org JSON-LD). It filters by title relevance + DACH location,
skips everything already in `state/seen.json` / `jobs.csv`, bumps `last_seen_date` / `status` of
known jobs, auto-adds newly seen employers to `companies.csv`, and queues at most `--max-new`
(default 200) postings ranked by what the dataset lacks (entry level, CH/AT, original company
postings, salary info; staffing agencies de-prioritised; max 3 per company). The rest stays as
backlog for the next run. Read `inbox/$D/manifest.json` for counts.

### 2. Web search (LLM, targeted — keep it to ~15–25 searches)
Covers what feeds miss — mainly **Switzerland** and companies without a public ATS feed.
- `python3 jobs.py queries --n 15` gives the next queries from a rotating matrix
  (role × city × entry-level word × site), never-tried first, so each run searches further.
  After each search: `python3 jobs.py log-query "<query>" --found <N new>`.
- **Indeed / LinkedIn / StepStone / XING / jobs.ch / Glassdoor: search snippets only.** Use the
  result title/snippet to learn *company + role*; never fetch those pages, never log in.
  Then find the original: `python3 jobs.py add-company "<Company>" --domain <domain>` (gets its
  ATS feed detected and fetched automatically from then on) and/or, if you found the employer's
  own posting URL, `python3 jobs.py add-url <url>` (extracts JSON-LD / trimmed text into
  `inbox/$D/batch_web.jsonl` — much cheaper than WebFetch).
- The search engine largely **ignores `site:` operators** — the snippets still name employers.
  Spend roughly a third of the searches on **company discovery** ("AI startups Zurich",
  "KI Startups Wien", "ML spin-offs Lausanne", funding-round news) and register every DACH
  AI/data employer found with `add-company --domain`; then run `jobs.py detect` *before*
  `jobs.py fetch` so new feeds are included in the same run. This compounds: each registered
  company is fetched for free on every future run. Log discovery queries with a `DISCOVERY:` prefix.
- Search-result posting URLs are often stale (~55% were 404 on 2026-11-24): register the company
  rather than relying on `add-url`.
- Prefer company career pages / ATS URLs (greenhouse.io, lever.co, ashbyhq.com, personio.de,
  smartrecruiters.com, workable.com, myworkdayjobs.com) in results — they are original postings.
- Follow "similar jobs" only when it is cheap; never bypass blocks (403, CAPTCHA, bot walls).

### 3. Extraction (Haiku subagents)
Spawn one `job-extractor` subagent (model haiku) per `inbox/$D/batch_*.jsonl` file (30 postings each; overhead is ~25k tokens per agent, so never shrink batches) (including
`batch_web.jsonl`), several in parallel. Each writes `batch_NN.out.jsonl`. The field spec and
rules live in `.claude/agents/job-extractor.md` — edit there, not here. If the agent type is not
available, use a general-purpose subagent with `model: haiku` told to follow that file.
Do **not** read the batch files yourself (that defeats the token savings).

### 4–5. Ingest + analyze
`jobs.py ingest` validates enums, canonicalizes skills (`pipeline/skills.py` alias map),
computes `job_id`, dedupes and appends; it prints problems — fix obvious ones, re-run is safe.
`jobs.py analyze` runs `analysis_gen.py` (do not bypass). Then add to `reports/$D.md` a short
"Web search" section: queries run, what worked/failed, notable finds.

## Data model
`jobs.csv` columns: job_id, job_title, normalized_role, seniority, seniority_basis, company,
location, country, work_type, salary_min/max/currency/period, required_skills,
nice_to_have_skills (semicolon-separated), years_experience, education_required,
language_requirements, posting_url, posting_date, source, first_seen_date, last_seen_date,
status (open / closed / unknown / unverified), is_active (yes / no / ? — 2nd column, derived
from status), active_checked_date. A posting is `open` when seen in a feed or confirmed by
`check-active` (ATS API where possible, else page check); `closed` on 404/410, redirect away
from the posting, "no longer available" notice, or expired JSON-LD; `unknown` when the site
blocks checks (403/429/bot wall) — never guessed. `open_jobs.md` lists all is_active = yes.

`job_id = sha1(normalized company | normalized title | primary city)[:12]` — distinct roles at
one company stay separate; the same posting seen via two sources collapses.

`companies.csv` — the company index: name, domain, careers_url, country, ats, ats_slug,
detect_status (found / guessed / none / manual; 'none' retried after 90 days), last_fetched,
relevant_open. Bulk import: `python3 jobs.py import-companies <file.csv>` then
`python3 jobs.py detect` (run in background; ~1 min per 70 companies).

`state/seen.json` — every posting URL ever queued (pending / ingested / rejected).
`state/search_log.json` — web-search queries tried and their yield.

## Scope rules
- Only roles physically in or remote-from CH/DE/AT. Any posting language; output in English.
- In scope: roles that build or apply AI/data systems technically, all levels incl. Intern /
  Werkstudent / Junior / Graduate / Trainee. Out: AI sales/marketing/consulting-only/product
  management, dual-study programmes, theses, training-course providers.
- Never fabricate salaries, skills or companies. Blank > guess. Only explicitly named skills.
- No logins, no paywalls, no CAPTCHA/bot-wall bypassing. Log unreachable sources in the report.
- One bad posting or source must not abort the run.

## Files
| File | Purpose |
|---|---|
| `jobs.py` | CLI entry point (fetch, add-url, ingest, analyze, import-companies, add-company, detect, queries, status) |
| `pipeline/` | fetchers (`ats.py`, `boards.py`), filters (`common.py`), `skills.py`, `ingest.py`, `companies.py`, `queries.py` |
| `analysis_gen.py` | regenerates the three deliverables from `jobs.csv` |
| `jobs.csv`, `companies.csv`, `state/` | persistent state |
| `skills_by_level.md`, `salary_benchmarks.md`, `reports/YYYY-MM-DD.md` | deliverables |
| `inbox/` | per-run work files (git-ignored) |
| `LEARNINGS.md` | source reliability + normalization notes; append what you learn |

## Cloud-run note
When run as a scheduled cloud agent: after the cycle, commit and push `jobs.csv`,
`companies.csv`, `state/`, `skills_by_level.md`, `salary_benchmarks.md` and `reports/<date>.md`.
