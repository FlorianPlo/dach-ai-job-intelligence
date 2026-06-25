# LEARNINGS — persistent skill memory for the DACH job-intelligence agent

Accumulated across runs. Append/update; do not delete history without reason.
Last audited: 2026-06-25 (self-improvement meta-run on Opus).

## Source reliability
- **Arbeitnow API** (`/api/job-board-api?page=N`) — works; structured JSON, DE-heavy.
  Quirk: the API `description` field is **empty** — must WebFetch each posting page to
  extract skills. Largest contributor so far (19 + 3 via recommended-jobs blocks).
- **datacareer.ch** (`/categories/machinelearning/`, `/datascience/`) — best CH source.
  Listing → `/job/<id>/` pages WebFetch cleanly. CH postings almost **never disclose salary**.
- **karriere.at** (`/jobs/<query>/wien`) — best AT source. Salaries shown, often **monthly,
  paid 14×/year**. URLs are `/jobs/<numeric-id>`.
- **swissdevjobs.ch** — HTTP 403, skip.
- **🚨 EGRESS PROXY BLOCKS ALL PRIMARY JOB BOARDS (2026-06-24).** In the scheduled cloud-agent
  environment the egress proxy policy now **rejects connections** (`connect_rejected`, policy
  denial) to every primary source:
    - `www.arbeitnow.com:443` — connect_rejected
    - `www.datacareer.ch:443` — connect_rejected
    - `www.karriere.at:443`   — connect_rejected
  Impact: the daily discovery step cannot reach its three best sources from this environment.
  This is a **critical reliability issue** for the automation, not a transient rate-limit.
  Mitigations to try, in order:
    1. **WebSearch** uses a different network pathway and still works — lean on it to discover
       postings, then attempt WebFetch on the original posting URL (may still be blocked if it
       resolves to a blocked domain; aggregator/company mirrors sometimes are not).
    2. **Company career pages** on unblocked domains (greenhouse.io, lever.co, ashbyhq.com,
       personio, workday, smartrecruiters, join.com, etc.) — many DACH employers post here and
       these hosts are often outside the block list. Prefer them over the blocked boards.
    3. If a domain you need is blocked, check `curl -sS "$HTTPS_PROXY/__agentproxy/status"` and
       `/root/.ccr/README.md` for whether an allowlist entry can be requested — do NOT disable
       TLS or unset HTTPS_PROXY.
    4. Log every blocked source in the daily report's "sources that failed" section so the gap
       in coverage is visible and the run stays explainable. Never silently produce a thin run.
  Until the policy changes, expect **WebSearch + unblocked career pages** to be the only viable
  discovery channels; treat arbeitnow/datacareer/karriere as unavailable.
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

## Data quality issues observed (2026-06-24 audit)
- **`country()` mis-parses multi-city locations.** `country(r)` returns the last comma-segment of
  `location`. Rows whose location has **no comma** but a slash (e.g. `Zurich/London`,
  `Heidelberg/Berlin`, `Munich/Berlin`) return the *whole string* as the "country", polluting the
  country mix (`{'Zurich/London': 1, 'Heidelberg/Berlin': 1, 'Munich/Berlin': 2, ...}`). This is
  an **extraction-side** issue: such rows should be stored as `"City, Country"` (pick the primary
  DACH city). Not fixed in analysis_gen.py — heuristically guessing the country from a slashed
  city string is unsafe (skip-if-unsure). Fix at extraction time; see backlog #6.
- **Future-dated `first_seen_date` rows exist.** jobs.csv currently holds rows first-seen on
  2026-06-25/-26/-27 (prior swarm runs were dated ahead of the real calendar). With
  `RUN=2026-06-24` these correctly fall outside both `prev` (first_seen < RUN) and `new_today`
  (first_seen == RUN), so they count toward N but not the delta. Not a bug in the script, but a
  reminder: **always pass the true run date**; mis-dated rows quietly distort the "new this run"
  count on the day their date matches RUN.
- **Read-time canon is exact-full-token (verified again on Opus).** Confirmed the 2026-06-24 alias
  additions do NOT clobber distinct compounds: `Azure OpenAI`/`Azure OpenAI Service`/`OpenAI Codex`
  stay distinct from the new bare `openai→OpenAI`; `LlamaIndex`/`LlamaParse`/`Llama 3` stay distinct
  from bare `llama→Llama`; `Google Cloud→GCP` and `powerbi→Power BI`/`vector databases→Vector
  Databases` merge correct case splits. `OpenAI API→OpenAI` is a deliberate fold (documented inline).
- **Defensive CSV read added (additive).** `analysis_gen.py` now normalizes every expected field to
  a string and skips a row only if it has *neither* `job_id` nor `job_title` (emitting a stderr
  warning). Verified the OLD direct-access code crashed with `AttributeError: 'NoneType' object has
  no attribute 'split'` on a ragged row; the new code survives it. Satisfies the quality rule
  "one bad posting must not abort the run." No change to jobs.csv or its schema.
- **Trend "falling" table was misleading on a growing dataset.** Skills whose absolute count
  held or rose (e.g. `Git` 6→6, `CI/CD` 8→10) showed as "falling" purely because total
  postings grew, diluting their share. Δpp is the right metric but needs a noise floor — see
  backlog #5 (now DONE).

## Data quality issues observed (2026-06-25 audit)
- **Pervasive case-only skill splits (the dominant count distortion).** At N=228 the raw
  `required_skills`/`nice_to_have_skills` tokens carried **~48 case-only collisions** — the
  identical skill differing ONLY by letter case, e.g. `Machine Learning` 43 / `machine learning` 17,
  `pandas` 8 / `Pandas` 5, `MLflow` 12 / `MLFlow` 1, `Computer Vision` 9 / `computer vision` 2 /
  `Computer vision` 1, `Data Pipelines` 5 / `data pipelines` 11 / `Data pipelines` 2,
  `Deep Learning` 18 / `deep learning` 8, `Generative AI` 14 / `generative AI` 1,
  `Vector Databases` 6 / `vector databases` 5, `Kubeflow`/`KubeFlow`, `ElasticSearch`/`Elasticsearch`,
  `FFmpeg`/`ffmpeg`, etc. The hand-maintained `_SKILL_ALIASES` case entries only covered a few of
  these. **Fixed in analysis (read-time, additive):** added a GENERIC case-fold pass — see audit log
  + backlog #8. This is an extraction-side hygiene problem too (postings should be normalized to a
  canonical casing when scraped); read-time fold is the safety net (backlog #1b still applies).
- **Slashed multi-city locations now resolved (read-time, additive).** The 4 comma-less slashed
  rows (`Munich/Berlin` ×2 = Helsing, `Zurich/London` = On AG, `Heidelberg/Berlin` = Aleph Alpha)
  that polluted the country mix are now mapped to their primary DACH country via a curated
  unambiguous city→country table applied ONLY to comma-less, slash-containing strings — see
  backlog #6 (now DONE in analysis). Country mix went from
  `{Germany 118, Switzerland 51, Austria 55, Munich/Berlin 2, Zurich/London 1, Heidelberg/Berlin 1}`
  to the clean `{Germany 121, Switzerland 52, Austria 55}`. Extraction should still store
  `"City, Country"` so the raw CSV is self-describing (backlog #6 extraction-side stays open).
- **Future-dated `first_seen_date` rows persist (not a bug, reminder).** jobs.csv holds rows
  first-seen 2026-06-26 (3) and 2026-06-27 (33) — ahead of today's real date 2026-06-25. With
  `RUN=2026-06-25` these count toward N (228) but fall outside both `prev` and `new_today`, so the
  "new this run" count is 10 (the genuine 2026-06-25 rows). Always pass the true calendar date.
- **jobs.csv parses clean.** 228 rows, 0 ragged, 0 empty `job_id`. Defensive read (2026-06-24)
  still in place and exercised.

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
6. **Location/country normalization** — DONE in analysis (2026-06-25), extraction-side still open.
   `analysis_gen.py` `country()` now resolves comma-less SLASHED multi-city strings via a curated
   UNAMBIGUOUS DACH city→country map (`_CITY_COUNTRY`), applied ONLY when the location has no comma
   and contains "/". `Zurich/London`→Switzerland, `Munich/Berlin`/`Heidelberg/Berlin`→Germany.
   Unrecognised slashed strings fall through to the exact prior behaviour (skip-if-unsure preserved),
   so this is additive/reversible and never guesses a non-DACH country. **Extraction-side fix still
   wanted:** store `location` as `"City, Country"` so the raw CSV is self-describing without the map.
7. **Discovery resilience under egress block (open, HIGH PRIORITY)** — primary boards are
   proxy-blocked in cloud (see Source reliability). Build a WebSearch-first discovery path plus a
   curated list of unblocked DACH career-page hosts (greenhouse/lever/ashby/personio/join.com).
   This is now the top operational risk for the daily run.

## Audit log
- **2026-06-24** (self-improvement meta-run on Opus): audited all deliverables at N=211 rows
  (211 valid rows, 10 first-seen on RUN=2026-06-24; jobs.csv parses clean with the stdlib csv
  reader — 0 ragged rows). Two additive, verified changes to `analysis_gen.py`; **jobs.csv and its
  schema untouched**:
  (1) **Expanded `_SKILL_ALIASES`** (backlog #1, additive). Added case-split + provider/lib aliases:
  `vector databases→Vector Databases` (real case split 5+6), `powerbi→Power BI`, `google cloud`/
  `google cloud platform→GCP`, `amazon web services→AWS`, `langchain→LangChain`,
  `llamaindex→LlamaIndex`, and future-proofing provider tokens `openai`/`openai api→OpenAI`,
  `anthropic→Anthropic`, `vllm→vLLM`, `mistral→Mistral`, `llama→Llama`. Verified via canon() unit
  checks that distinct compounds survive: `Azure OpenAI`, `Azure OpenAI Service`, `OpenAI Codex`,
  `Apache Spark`, `PySpark`, `SparkML`, `Vision Transformers`, `LlamaParse`, `Llama 3`,
  `Torch Distributor`, `torch.distributed` all unchanged. (`OpenAI API→OpenAI` is a deliberate fold.)
  (2) **Defensive CSV read** (additive, satisfies "one bad posting must not abort the run"). Rows
  are normalized field-by-field to strings; a row is skipped (with stderr warning) only if it lacks
  BOTH job_id and job_title. Proved the prior direct-access code crashed (`AttributeError: 'NoneType'
  ... 'split'`) on a ragged row built in a scratch dir; new code survives and completes.
  Tested `python3 analysis_gen.py <RUN_DATE>` on RUN=2026-06-24, 2026-06-27, and 1900-01-01
  (prev=0/new=0 path) — all three deliverables generate clean on every path.
  Did NOT change: salary/FX logic (backlog #3 still blocked on no CH data), location parsing
  (backlog #6 — extraction-side, unsafe to guess in analysis), trend logic (already sound).
  **Critical operational finding logged separately:** the egress proxy now blocks arbeitnow,
  datacareer.ch, and karriere.at outright (connect_rejected) — see Source reliability + backlog #7.
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
