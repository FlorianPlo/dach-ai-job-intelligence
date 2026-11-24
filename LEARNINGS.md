# LEARNINGS — persistent skill memory for the DACH job-intelligence agent

Accumulated across runs. Append/update; do not delete history without reason.
Last audited: 2026-06-23 (self-improvement meta-run).

## Source reliability (updated 2026-11-24, pipeline rebuild)
- **Bundesagentur für Arbeit API** — `rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v6/jobs`
  with header `X-API-Key: jobboerse-jobsuche`. Biggest DE source (~1.5k hits/month for our
  queries). Details via `pc/v4/jobdetails/<base64(refnr)>` (v6 details = 403). Detail endpoint
  drops requests above ~3 parallel. Filter `stellenangebotsart == ARBEIT` (else dual study).
  Postings with `externeUrl` have no description -> fetch employer page JSON-LD. Also lists CH/AT.
- **Arbeitnow API** now returns the description (HTML-escaped) — no page fetch needed. It also
  carries FR/NL/UK jobs: always apply the DACH filter.
- **karriere.at** — listing HTML gives `/jobs/<id>` links; each posting page has a clean
  schema.org JobPosting JSON-LD incl. `baseSalary`.
- **datacareer.ch** — since ~Nov 2026 behind a DataDome CAPTCHA wall (403). Do not bypass;
  CH coverage now comes from company ATS feeds + web search.
- **Company ATS feeds** (Greenhouse/Lever/Ashby/Personio/Recruitee/SmartRecruiters/Workable/
  Workday) — public JSON/XML, fastest and cheapest. Slug guesses are only accepted if the feed
  contains a DACH posting. Lever has a separate EU host (`api.eu.lever.co`).

- **Web search (2026-11-24):** `site:` operators are largely ignored — don't rely on them. Use
  search for *company discovery* (snippets) and register companies; ~55% of posting URLs from
  search results were already 404. Haiku extractor overhead ≈25k tokens/agent → keep batches at 30.
- **Company-discovery searches** (startup lists, funding news) give the best yield per search:
  4–8 DACH employers each, ~40% of which turn out to have a public ATS feed.
- **AMS syndication in BA feed:** refs `11949-…` carry the occupation as title (security jobs as
  "Data Engineer"). fetch.py requires data/ML terms in their body text.
- **Slug guessing:** never guess with only the first word of a multi-word company name.
- **Arbeitnow** expanded to UK/FR/CH (Nov 2026) — location strings need the NON_DACH check.

### Older notes
- **Arbeitnow API** (`/api/job-board-api?page=N`) — works; structured JSON, DE-heavy.
  Quirk: the API `description` field is **empty** — must WebFetch each posting page to
  extract skills. Largest contributor so far (19 + 3 via recommended-jobs blocks).
- **datacareer.ch** (`/categories/machinelearning/`, `/datascience/`) — best CH source.
  Listing → `/job/<id>/` pages WebFetch cleanly. CH postings almost **never disclose salary**.
- **karriere.at** (`/jobs/<query>/wien`) — best AT source. Salaries shown, often **monthly,
  paid 14×/year**. URLs are `/jobs/<numeric-id>`.
- **swissdevjobs.ch** — HTTP 403, skip.
- **LinkedIn / Indeed / StepStone / Glassdoor** — auth/aggregator; use only to discover
  company names, never fetch postings (per spec).
- Coverage gaps: Junior level is very thin (n=1); pure Data Scientist and Lead/Principal
  were underrepresented early. Switzerland discloses no salary → salary table is EUR/DE/AT only.

## Extraction & normalization rules
- Normalize all output to **English** regardless of posting language.
- **Canonical skill spellings** (pick the left form; map variants on the right):
  - `scikit-learn` (not "sklearn")
  - `PyTorch` (not "torch"); keep `Torch Distributor` separate (distinct tool)
  - `TensorFlow`; keep `TensorRT` separate (distinct)
  - `Hugging Face` (not "huggingface"/"HF")
  - `Azure` — collapse "Microsoft Azure" → "Azure"; keep sub-services explicit
    (`Azure OpenAI`, `Azure Data Factory`, `Azure Synapse`, `Azure SQL`).
  - `Spark` — keep `PySpark` and `SparkML` distinct (they are specific); but do not also
    emit a bare "Spark" when only PySpark is mentioned.
  - `RAG` — keep `GraphRAG` distinct.
  - `LLMs` — prefer one umbrella spelling; avoid emitting both "LLM" and "LLMs" for the
    same posting. Specific concepts (`LLM Fine-Tuning`, `LLMOps`, `LLM Evals`) stay distinct.
  - `CI/CD` (with slash, uppercase).
  - `Kubernetes` (not "k8s").
- Only record skills **explicitly named** in the posting. Blank > guess. Never fabricate.
- **Seniority heuristic (years → level)** — make CLAUDE.md mapping concrete:
  - Intern/Working-Student/Trainee → enrollment or "Werkstudent/Praktikum" signal.
  - Junior → 0–2 yrs, or title says Junior/Graduate/Absolvent/Berufseinsteiger.
  - Mid → 2–5 yrs, IC scope, no leadership.
  - Senior → 5+ yrs or "Senior" title + architecture/ownership scope.
  - Lead/Principal → team leadership, principal/staff scope, or "Lead/Head".
  - When years conflict with title, prefer the **scope** signal and explain in `seniority_basis`.

## Known dedup behavior
- Since 2026-11-24: `job_id = sha1(norm company | norm title | primary city)[:12]` (migrated all
  existing rows, 0 collisions). Distinct roles no longer collapse. Old formula
  (company+normalized_role+location) is retired.
- On re-seeing an existing `job_id`: skip insert, bump `last_seen_date`. Append-only otherwise.

## Improvement backlog (prioritized)
1. ~~**Skill canonicalization at extraction time**~~ DONE in code (`pipeline/skills.py`, applied by ingest).
   Original note: **Skill canonicalization at extraction time** — apply the alias map above when writing
   `required_skills`/`nice_to_have_skills` so counts don't split across variants
   (Azure vs Microsoft Azure, etc.). Highest analytical impact.
2. **Salary annualisation fidelity** — DONE: hourly ×40×52; AT monthly now ×14 (2026-11-24). Old note: AT monthly
   should arguably be ×14 (not ×12) to match 13th/14th salary convention; currently ×12
   (conservative). Decide and document one convention.
3. **CHF/EUR FX** — the median-by-role table only pools EUR rows. Add a fixed documented
   FX rate (or exclude with a note) so CH salaries, if ever disclosed, are comparable.
4. **Junior coverage** — actively query Junior/Graduate vocabulary each run; n=1 today.
5. **Trend robustness** — DONE: MIN_TREND=3 threshold in analysis_gen.py. Old note: consider min-count threshold
   so 1-job noise (n=1 churn) doesn't dominate the falling table on a small dataset.
