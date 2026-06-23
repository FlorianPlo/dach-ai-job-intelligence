# LEARNINGS — persistent skill memory for the DACH job-intelligence agent

Accumulated across runs. Append/update; do not delete history without reason.
Last audited: 2026-06-23 (self-improvement meta-run).

## Source reliability
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

## Data quality issues observed (2026-06-23 audit)
- **Azure alias splitting counts — now fixed in analysis (read-time).** `jobs.csv` holds both
  `Azure` (18) and `Microsoft Azure` (4) as separate raw tokens (and similarly
  `machine learning` 17 vs `Machine Learning` 15, `LLMs` 22 vs `Large Language Models` 5,
  `Generative AI` 6 vs `GenAI` 3). As of the 2026-06-23 swarm run, `analysis_gen.py` applies an
  **in-memory alias map at read time** (`canon()` / `_SKILL_ALIASES`) so counts no longer split
  — Azure → 18→22 merged, Machine Learning → 31, LLMs → 27, Generative AI → 10. The CSV itself is
  still NOT rewritten (deliberate; the script must not mutate source data). A belt-and-suspenders
  fix at extraction time (write canonical tokens to the CSV) remains desirable so the raw data is
  clean too — see backlog #1b.
- **Matching is exact full-token, case-insensitive — NOT substring.** This is load-bearing:
  collapsing on substring would wrongly merge `LLM APIs`, `LLM Fine-Tuning`, `LLMOps`,
  `Azure OpenAI`, `Torch Distributor`, `torch.distributed`, `GraphRAG`, `PySpark`, `SparkML`.
  Verified post-change that all of these survive as distinct tokens. When adding a new alias,
  add a lowercased full-token key to `_SKILL_ALIASES`; never switch to substring matching.
- **Case-collapse is doing real work.** The biggest single split in the current data was casing
  (`machine learning`/`Machine Learning`, `deep learning`/`Deep Learning`,
  `generative AI`/`Generative AI`), not spelling. These are merged to the Title-Case canonical.
  Tokens not in the map keep their original casing (unknown tokens pass through `canon()` unchanged).
- **`Spark` vs `PySpark`/`SparkML`** remain intentionally distinct (kept).
- **Trend "falling" table was misleading on a growing dataset.** Skills whose absolute count
  held or rose (e.g. `Git` 6→6, `CI/CD` 8→10) showed as "falling" purely because total
  postings grew, diluting their share. Δpp is the right metric but needs a noise floor — see
  backlog #5 (now DONE).

## Known dedup behavior
- `job_id = hash(company + normalized_role + location)`. **Intentionally collapses** distinct
  postings sharing those three (e.g. Estateanfrage "Werkstudent AI Engineer" vs "AI Engineer
  Trainee", both Munich/AI Engineer → one row kept). Not a bug. When it happens, note the
  dropped role in the daily report so the count is explainable.
- On re-seeing an existing `job_id`: skip insert, bump `last_seen_date`. Append-only otherwise.

## Improvement backlog (prioritized)
1. **Skill canonicalization at read time in analysis_gen.py** — DONE (2026-06-23 swarm run).
   `analysis_gen.py` now applies `_SKILL_ALIASES` via `canon()` to both `required_skills` and
   `nice_to_have_skills` at read time, in memory only (CSV untouched). Merges
   Microsoft Azure→Azure, sklearn→scikit-learn, torch→PyTorch, k8s→Kubernetes, HF/huggingface/
   Hugging Face Transformers→Hugging Face, LLM/Large Language Models→LLMs, GenAI→Generative AI,
   tensorflow→TensorFlow, plus case-collapses (machine learning→Machine Learning,
   deep learning→Deep Learning). Distinct compounds preserved (verified). Highest analytical impact.
1b. **Skill canonicalization at EXTRACTION time (still open)** — also write canonical tokens to
   `jobs.csv` when scraping, so the raw data is clean for any consumer, not just this script.
   Read-time canon is the safety net; extraction-time is the source-of-truth fix.
2. **Salary annualisation fidelity** — DONE (2026-06-23 swarm run). Hourly ×40×52 (earlier).
   AT monthly EUR now annualised **×14** (13th/14th-salary convention; 22 AT rows affected),
   all other monthly stays ×12. Convention is documented inline in `annual()` and in the
   salary_benchmarks.md caveat note. Decision locked: ×14 for AT-EUR-monthly only.
3. **CHF/EUR FX** — STILL OPEN. The median-by-role table only pools EUR rows; CH discloses no
   salary yet so no CHF rows exist to convert. When the first CHF salary appears, adopt a fixed
   documented rate (suggest **1 CHF = 1.05 EUR**, pinned in this file and re-checked quarterly)
   rather than a live FX lookup, so runs are reproducible. Until then, EUR-only pooling stands.
   Not implemented now because there is no CHF data to test against (skip-if-unsure rule).
4. **Junior coverage** — actively query Junior/Graduate vocabulary each run; n=1 today.
5. **Trend robustness** — DONE (2026-06-23): `analysis_gen.py` now applies a noise-floor
   `MIN_TREND_COUNT = max(2, round(N/40))` to the rising/falling Δpp tables, so a skill must
   appear in at least that many postings (prev or current) to be ranked. New/disappeared
   skills are still listed separately, so nothing is hidden. Threshold scales with dataset
   size (e.g. N=79 → 2, N=200 → 5). At current N the effect is modest but grows with data.

## Audit log
- **2026-06-23** (self-improvement SWARM run): audited all deliverables at N=152 rows
  (152 total, 80 first-seen this run). Implemented two backlog items, both additive and verified:
  (1) **backlog #1** — read-time skill canonicalization in `analysis_gen.py` (`canon()` +
  `_SKILL_ALIASES`), applied to required & nice-to-have skills, CSV untouched. Effect on the
  overall top-skills table: `Machine Learning` 16→31 (absorbs lowercase variant),
  `Azure` 14→18 (absorbs `Microsoft Azure`), `LLMs` 22→23, `Generative AI`→9, `Deep Learning`→11.
  Confirmed distinct compounds survive (`LLM APIs`, `LLM Fine-Tuning`, `Azure OpenAI`,
  `torch.distributed`, `Torch Distributor`, `PySpark`, `SparkML`, `GraphRAG`).
  (2) **backlog #2** — AT EUR monthly salaries now annualised ×14 (22 rows affected); all other
  monthly ×12; documented inline. Tested `python3 analysis_gen.py <RUN_DATE>` on a scratch copy
  with three run dates (2026-06-23, future 2026-06-27, and 1900-01-01 where new=0) — all three
  deliverables generate clean on every path; no schema/column change to jobs.csv.
  Did NOT implement backlog #3 (CHF/EUR FX): no CH salary data exists to test against, so per the
  skip-if-unsure rule it is documented (proposed pinned rate 1 CHF = 1.05 EUR) rather than coded.
  Data-quality note: case-splitting (not spelling) was the single largest count distortion in the
  current dataset — worth catching at extraction time too (backlog #1b).
- **2026-06-23** (self-improvement meta-run): audited all deliverables at N=79/80 rows.
  Implemented backlog #5 (trend noise floor) — additive, all 3 outputs still generate and
  `python3 analysis_gen.py <RUN_DATE>` runs clean (verified on a scratch copy with both a
  2026-06-23 and a 2026-06-27 run date). Documented the live `Azure`/`Microsoft Azure` count
  split as an extraction-time bug (backlog #1, still open — highest-impact remaining item).
  Did not touch backlog #2/#3/#4 (each needs a data/convention decision, not just code).
