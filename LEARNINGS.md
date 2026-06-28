# LEARNINGS — persistent skill memory for the DACH job-intelligence agent

Accumulated across runs. Append/update; do not delete history without reason.
Last audited: 2026-06-28 (self-improvement meta-run on Opus).

## Data quality issues observed (2026-06-28 audit)
- **Database stats:** **407 rows**, **0 duplicate `job_id`**, **0 empty `job_id`**, **0 ragged
  rows**. Unchanged in size since the 2026-06-27 audit (no swarm discovery ran in between).
  `first_seen_date` distribution:
  `{2026-06-22: 16, 2026-06-23: 139, 2026-06-24: 27, 2026-06-25: 80, 2026-06-26: 58, 2026-06-27: 87}`.
  Note there are **NO rows dated 2026-06-28**, so with `RUN=2026-06-28` the genuine "new this run"
  count is **0** and all 407 rows fall into `prev` (first_seen < RUN). Seniority mix
  `{Mid 118, Senior 116, Intern 86, Junior 65, Lead/Principal 22}`; role mix
  `{Data Scientist 126, ML Engineer 95, AI Engineer 84, Data Engineer 66, AI Researcher 34, Other 2}`;
  work_type mix `{Hybrid 280, Onsite 105, Remote 22}`.
- **`python3 analysis_gen.py 2026-06-28` runs clean (EXIT 0, N=407, new=0)** both BEFORE and AFTER
  the changes. All three deliverables regenerate. Also re-verified in a scratch copy on
  RUN=2026-06-27 (new=87, full breakdown path) and RUN=1900-01-01 (prev=0 first-run path) — all
  three deliverables generate on every path.
- **NEW alias added: `apache kafka → Kafka`.** The raw data carried `Apache Kafka` (2) split from
  `Kafka` (13); the generic `_CASE_MAP` cannot merge them (they differ by a vendor prefix, not just
  case). This is the exact same Apache vendor-prefix fold already applied to `apache spark→Spark`
  and `apache airflow→Airflow`, so it is a safe, consistent additive entry. Effect: `Kafka`
  consolidated to **15** postings (was 13). Verified `Kafka Streams` (distinct compound) survives
  unchanged — fold is full-token, not substring.
- **NEW: empty-run guard in the daily report (additive output fix).** When a run adds no jobs
  (new=0, e.g. running on a calendar date with no matching `first_seen_date` rows — exactly today's
  situation), the report's "By country / By role / By seniority" lines rendered as bare labels with
  nothing after them, and "## Notable new postings" was a dangling header with no content. The
  report now emits an explicit "_No new jobs were added in this run…_" note instead, telling the
  reader to check that discovery ran and new rows carry `first_seen_date = RUN`. The new>0 path is
  byte-for-byte unchanged (verified on RUN=2026-06-27 → full breakdown + 6 notable postings).
- **Skill canonicalization otherwise complete at N=407.** Ran every token through the live `canon()`
  and clustered residuals by punctuation/space/case: the only remaining "near-duplicate" clusters
  are genuine distinct skills that must NOT merge — `C++`/`C#` (different languages),
  `AI Automation`/`AI/Automation` and `Multimodal AI`/`multi-modal AI` (n=1 each, ambiguous, left
  split per skip-if-unsure). All real case-only splits (`Machine Learning`/`machine learning` 64+43,
  `Computer Vision`/`computer vision`, `Power BI`/`PowerBI`, `Pandas`/`pandas`, `Transformers`/
  `transformers`, `Graph Neural Networks`/`graph neural networks`, `Statistics`/`statistics`, etc.)
  are still absorbed by `_CASE_MAP`. **`GCP Vertex AI` (2) left distinct from `Vertex AI` (3)**
  deliberately — sub-service tokens stay distinct per the documented Azure/GCP sub-service rule
  (mirrors `Azure OpenAI`/`AWS Bedrock` staying separate); not folded.
- **`country()` resolution clean at N=407.** Country mix `{Germany 221, Switzerland 101, Austria 85}`,
  zero non-DACH/leftover buckets across 76 distinct location strings. All comma-less specials still
  resolve: slashed (`Zurich/London→Switzerland`, `Munich/Berlin`/`Heidelberg/Berlin→Germany`), bare
  `Germany`, and `Germany (Remote)→Germany` (parenthetical strip). No new `_CITY_COUNTRY` entries
  needed. (Aesthetic-only: `Dusseldorf`/`Düsseldorf` and `Garching`/`Garching bei München`/`Grodig`/
  `Grödig` are city-name spelling variants but all carry the correct `, Germany`/`, Austria` country
  suffix, so the country mix is unaffected — no fix warranted; city-level normalization is out of
  scope.)
- **No seniority assignment errors found.** Title↔level scan flagged no new conflicts beyond the
  defensible ones noted in prior audits. The `order` list and the §4 high/low split
  (Intern/Junior/Mid = lower, Senior/Lead-Principal = higher) remain correct.
- **CHF/EUR FX (backlog #3) still blocked.** 0 CHF salary rows; Switzerland still discloses no salary.
  Pinned-rate plan (1 CHF = 1.05 EUR) stays documented for the first CHF row.
- **Discovery resilience (backlog #7) remains the top operational risk.** Egress proxy still
  expected to block arbeitnow/datacareer/karriere in cloud; WebSearch + unblocked career-page hosts
  remain the only viable channels. No allowlist change attempted (out of scope for this additive
  audit). The N=407 plateau since 2026-06-27 (no new rows) is consistent with a discovery gap and is
  exactly what the new empty-run report note is designed to make visible.

## 2026-06-27 audit (Opus self-improvement agent)
- **jobs.csv parses clean at N=407.** 408 lines (1 header), **0 duplicate `job_id`**, **0 rows
  with empty `job_id`**, **0 ragged rows**. `first_seen_date` distribution:
  `{2026-06-22: 16, 2026-06-23: 139, 2026-06-24: 27, 2026-06-25: 80, 2026-06-26: 58, 2026-06-27: 87}`.
  Grew 298 → 407 since the 2026-06-26 audit. With `RUN=2026-06-27` the genuine "new this run"
  count is **87** (the rows dated 2026-06-27 are now the real calendar date, so no future-dating
  this run). Seniority mix `{Mid 118, Senior 116, Intern 86, Junior 65, Lead/Principal 22}`;
  role mix `{Data Scientist 126, ML Engineer 95, AI Engineer 84, Data Engineer 66, AI Researcher 34, Other 2}`.
- **`python3 analysis_gen.py 2026-06-27` runs clean (EXIT 0, N=407, new=87)** both BEFORE and AFTER
  the change. All three deliverables (skills_by_level.md, salary_benchmarks.md, reports/2026-06-27.md)
  regenerate.
- **NEW: added 14 punctuation/spacing/vendor-prefix skill aliases the case-fold cannot catch.**
  `_CASE_MAP` only merges byte-identical-once-lowercased tokens, so splits that differ by
  spacing/hyphen/vendor-prefix stayed separate. Added to `_SKILL_ALIASES` (all full lowercased
  tokens, additive): `apache airflow→Airflow` (8+18), `apache spark→Spark` (6+34),
  `amazon sagemaker`/`aws sagemaker→SageMaker` (vendor-prefix fold, mirrors Microsoft Azure→Azure),
  `datamesh→Data Mesh`, `datavault→Data Vault`, `ms-sql→MS SQL`,
  `infrastructure-as-code→Infrastructure as Code`, `time-series forecasting`/`time series
  forecasting→Time Series Forecasting`, `time-series analysis`/`time series analysis→Time Series
  Analysis`, `restful api→REST API`, `restful apis→REST APIs`. Verified via `canon()` that distinct
  compounds survive (full-token, not substring): `Spark Streaming`, `SparkML`, `SparkSQL`, `PySpark`,
  `AWS Bedrock`, `AWS Lambda`, `GCP Vertex AI`, `Azure Data Factory`, `Azure OpenAI`, `GraphRAG`,
  `RAG`, `LLM Fine-Tuning` all unchanged. Effect in output: `Airflow` consolidated to 19 postings.
- **Generic `_CASE_MAP` still absorbing all case-only splits at N=407.** Found ~78 case-only
  collisions in the raw tokens (e.g. `Machine Learning` 64/`machine learning` 43, `Deep Learning`
  27/22, `Generative AI` 34/`generative AI` 6, `Pandas` 16/`pandas` 11, `MLflow` 23/`MLFlow` 1,
  `data pipelines` 27+5+2, `Computer Vision` 15+11+1, `prompt engineering` 12+9+2, `fine-tuning`
  8+1+1, `statistics` 13/`Statistics` 4, `Kubeflow`/`KubeFlow`, `Elasticsearch`/`ElasticSearch`,
  `ffmpeg`/`FFmpeg`, `Autogen`/`AutoGen`). All folded automatically; no hand-edits needed.
- **No seniority assignment errors found.** Substring scan for title↔level conflicts flagged only
  4 rows, all defensible: "Member of Technical Staff …" (vendor IC title, "Staff" ≠ Staff-level),
  "Data Science Trainee (… Future Leaders)" (program name, Trainee→Junior correct), and two
  "(Senior) Data Engineer" rows where the parenthetical "(Senior)" is optional/preferred so the
  conservative Mid call is fine. Seniority inference in the script itself (the `order` list and the
  high/low split in §4) is correct — Intern/Junior/Mid = "lower", Senior/Lead/Principal = "higher".
- **`country()` resolution clean at N=407.** Country mix `{Germany 221, Switzerland 101, Austria 85}`,
  zero non-DACH/leftover buckets. All 10 comma-less locations resolve correctly: slashed
  (`Zurich/London→Switzerland`, `Munich/Berlin`/`Heidelberg/Berlin→Germany`), bare `Germany`, and
  `Germany (Remote)→Germany` (parenthetical strip). No new `_CITY_COUNTRY` entries needed.
- **CHF/EUR FX (backlog #3) still blocked.** Switzerland still discloses no salary; all disclosed
  salary rows remain EUR. Pinned-rate plan (1 CHF = 1.05 EUR) stays documented for the first CHF row.
- **Discovery resilience (backlog #7) remains the top operational risk.** Egress proxy still blocks
  arbeitnow.com / datacareer.ch / karriere.at (`connect_rejected`) in cloud — CLAUDE.md's "Sources
  known to work" section is now stale for the cloud-agent environment and should be read together
  with this LEARNINGS note: in cloud, treat those three as UNAVAILABLE and rely on WebSearch +
  unblocked career-page hosts (greenhouse.io, lever.co, ashbyhq.com, smartrecruiters, join.com,
  personio, workday). No allowlist change attempted (out of scope for this additive audit).
- **Backlog #1b (extraction-time canonical tokens) still the recommended source-of-truth fix.** The
  read-time `_SKILL_ALIASES` + `_CASE_MAP` is the safety net; writing canonical skill spellings AND
  casing into jobs.csv at scrape time would clean the raw data for any consumer. The growing alias
  map (now ~50 entries) is a symptom that extraction-side normalization is overdue.

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

## Data quality issues observed (2026-06-26 audit)
- **Database size:** 298 rows, **0 ragged**, **0 empty `job_id`**, **0 duplicate `job_id`**. Grew
  228 → 298 since the 2026-06-25 audit. `first_seen_date` distribution:
  `{2026-06-22: 16, 2026-06-23: 139, 2026-06-24: 27, 2026-06-25: 80, 2026-06-26: 3, 2026-06-27: 33}`.
  With `RUN=2026-06-26` the genuine "new this run" count is **3**; the 33 rows dated 2026-06-27 are
  future-dated (prior swarm runs ahead of the calendar) and correctly fall outside both `prev` and
  `new_today`, counting toward N only. Always pass the true calendar date (reminder, not a bug).
- **NEW bug found & FIXED (read-time, additive): parenthetical-suffix country leak.** `country()`
  returned the raw last comma-segment, so a row stored as `"Germany (Remote)"` (no comma) leaked
  into the country mix as its OWN bucket: `{Germany 156, Switzerland 73, Austria 68, Germany (Remote) 1}`.
  Same class of bug as the slashed-cities issue fixed on 2026-06-25, just with a `(...)` suffix instead
  of a `/`. **Fix:** `country()` now strips a trailing `"(...)"` from the resolved last segment ONLY
  when the remainder is an exact DACH country name (`Germany`/`Switzerland`/`Austria`); any other case
  falls through to the exact prior behaviour (skip-if-unsure preserved — never guesses a non-DACH
  country, and rows like `"Berlin (Remote)"` still keep their comma and resolve via the last segment).
  Country mix is now clean `{Germany 157, Switzerland 73, Austria 68}`. Scope verified: this was the
  ONLY parenthetical last-segment in the dataset. jobs.csv untouched (extraction should still store a
  clean `"City, Country"` — backlog #6 extraction-side stays open).
- **Case-only splits all absorbed by the generic case-fold (verified again at N=298).** Found ~60
  case-only collisions in the raw tokens (e.g. `Machine Learning` 48 / `machine learning` 33,
  `Deep Learning` 20 / `deep learning` 18, `Generative AI` 18 / `generative AI` 5, `pandas` 8 /
  `Pandas` 12, `MLflow` 16 / `MLFlow` 1, `data pipelines` 21 / `Data Pipelines` 5 / `Data pipelines` 2,
  `agentic AI`/`Agentic AI`, `AutoGen`/`Autogen`, `ElasticSearch`/`Elasticsearch`, `KubeFlow`/`Kubeflow`,
  `FFmpeg`/`ffmpeg`). All are folded to the most-frequent casing by `_CASE_MAP`; no hand-edits needed.
  Note: a few fold to a lowercase canonical because the lowercase casing is genuinely the most frequent
  (`data pipelines` 21>7, `agentic AI`) — correct by the documented "most-frequent casing wins" rule,
  just aesthetically lowercase. Extraction-side canonical casing (backlog #1b) remains the source fix.
- **No new `_SKILL_ALIASES` entries warranted.** Checked the live synonym pairs (`GenAI`/`Generative AI`,
  `Large Language Models`/`LLMs`, `Google Cloud`/`GCP`, `sklearn`, `k8s`, `HF`/`huggingface`, etc.) —
  all already covered. `Azure ML` (n=1) kept distinct from `Azure` per the sub-service rule. Adding
  more low-frequency aliases would be noise; left unchanged.
- **CHF/EUR FX (backlog #3) still blocked: 0 CHF salary rows.** 66 rows disclose pay, **all EUR**;
  Switzerland still discloses no salary. No CHF data to test against → not implemented (skip-if-unsure).
  Pinned-rate plan (1 CHF = 1.05 EUR) stays documented for when the first CHF salary appears.
- **Junior coverage (backlog #4) much improved.** Seniority mix now
  `{Mid 87, Senior 88, Intern 59, Lead/Principal 18, Junior 46}` — Junior n=46 (was n=1 in early
  audits) and Intern n=59. Entry-level vocabulary targeting is clearly working; backlog #4 can be
  considered largely addressed, keep querying Junior/Graduate/Working-Student terms each run.
- **Discovery resilience (backlog #7) still the top operational risk.** Egress proxy still blocks
  arbeitnow/datacareer/karriere (connect_rejected) in cloud; WebSearch + unblocked career-page hosts
  remain the only viable channels. No allowlist change attempted (out of scope for this additive audit).

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
   so this is additive/reversible and never guesses a non-DACH country. **Extended 2026-06-26:**
   `country()` also strips a trailing work-mode parenthetical (e.g. `"Germany (Remote)"` → `Germany`)
   ONLY when the remainder is an exact DACH country name, fixing a 1-row leak into the country mix.
   **Extraction-side fix still wanted:** store `location` as `"City, Country"` so the raw CSV is
   self-describing without the map.
7. **Discovery resilience under egress block (open, HIGH PRIORITY)** — primary boards are
   proxy-blocked in cloud (see Source reliability). Build a WebSearch-first discovery path plus a
   curated list of unblocked DACH career-page hosts (greenhouse/lever/ashby/personio/join.com).
   This is now the top operational risk for the daily run.
8. **Generic case-fold canonicalization** — DONE (2026-06-25). `analysis_gen.py` now derives, per
   lowercased skill token, the most-frequently-seen casing in the dataset and folds all other
   casings to it (`_build_case_map()` / `_CASE_MAP`), applied AFTER the explicit `_SKILL_ALIASES`
   so curated decisions win. Generalises the hand-added case entries to ALL case-only splits
   (~48 found at N=228). Cannot merge distinct skills (collapse requires byte-identical lowercased
   tokens). Extraction-time canonical casing (backlog #1b) remains the source-of-truth fix.

## Audit log
- **2026-06-28** (self-improvement meta-run on Opus): audited analysis_gen.py, LEARNINGS.md,
  jobs.csv (**407 rows, 0 ragged, 0 empty job_id, 0 duplicate job_id**), skills_by_level.md,
  salary_benchmarks.md, reports/2026-06-27.md. Database unchanged in size since the 2026-06-27
  audit (no swarm discovery between runs); **no rows dated 2026-06-28**, so RUN=2026-06-28 yields
  new=0. Confirmed `python3 analysis_gen.py 2026-06-28` runs clean (EXIT 0, N=407, new=0) BEFORE
  and AFTER the changes; re-verified in a scratch copy on RUN=2026-06-27 (new=87, full breakdown
  path) and RUN=1900-01-01 (prev=0 first-run path) — all three deliverables generate on every path.
  **Two additive, verified changes to `analysis_gen.py`; jobs.csv and its schema untouched:**
  (1) **New skill alias `apache kafka → Kafka`** (backlog #1, additive). The raw data split
  `Apache Kafka`(2) from `Kafka`(13); `_CASE_MAP` can't merge them (vendor prefix, not case). Exact
  parallel to the existing `apache spark→Spark` / `apache airflow→Airflow` folds. Effect: `Kafka`
  consolidated to 15. Verified `Kafka Streams` (distinct compound) survives — full-token, not
  substring.
  (2) **Empty-run guard in the daily report** (output quality, additive). When new=0 the report's
  breakdown lines rendered as bare labels and "Notable new postings" was a dangling empty header;
  now it emits an explicit "no new jobs this run" note pointing the reader to check discovery / the
  `first_seen_date = RUN` invariant. The new>0 path is unchanged (verified on RUN=2026-06-27 →
  full breakdown + 6 notable postings render identically).
  Did NOT change: the generic `_CASE_MAP` (still absorbs all case-only splits — verified no new
  case splits at N=407); `GCP Vertex AI` kept distinct from `Vertex AI` per the sub-service rule;
  salary/FX logic (backlog #3 still blocked — 0 CHF rows); trend logic; the defensive CSV read; the
  dedup formula; `country()` (clean mix `{Germany 221, Switzerland 101, Austria 85}`, no new
  `_CITY_COUNTRY` entries needed). Backlog status: #7 (discovery resilience under egress block)
  confirmed STILL the top operational risk — the N=407 plateau since 2026-06-27 (zero new rows) is
  consistent with a discovery gap, which the new empty-run report note now surfaces explicitly.
- **2026-06-26** (self-improvement meta-run on Opus): audited analysis_gen.py, LEARNINGS.md,
  jobs.csv (**298 rows, 0 ragged, 0 empty job_id, 0 duplicate job_id**), skills_by_level.md,
  salary_benchmarks.md, recent reports. Confirmed `python3 analysis_gen.py 2026-06-26` runs clean
  (EXIT 0, N=298, new=3) BEFORE and AFTER the change; also re-verified in a scratch copy on
  RUN=1900-01-01 (prev=0 first-run path) and RUN=2026-06-27 (future) — all three deliverables
  generate on every path. **One additive, verified change to `analysis_gen.py`; jobs.csv and its
  schema untouched:**
  (1) **Parenthetical-suffix country resolution** (extends backlog #6, analysis side). `country()`
  now strips a trailing `"(...)"` from the resolved last comma-segment ONLY when the remainder is an
  exact DACH country name, then returns it. Fixes `"Germany (Remote)"` leaking into the country mix as
  its own bucket: mix cleaned from `{Germany 156, Switzerland 73, Austria 68, Germany (Remote) 1}` →
  `{Germany 157, Switzerland 73, Austria 68}`. Guard ensures it never alters a currently-correct
  output and never guesses a non-DACH country; unrecognised parentheticals fall through to the exact
  prior behaviour. Scope-checked: this was the only such row in the dataset. Read-time only; CSV not
  rewritten.
  Did NOT change: skill canonicalization (the generic `_CASE_MAP` already absorbs all ~60 case-only
  splits at N=298, and all live synonym pairs are already in `_SKILL_ALIASES` — no new aliases
  warranted; `Azure ML` n=1 kept distinct per sub-service rule), salary/FX logic (backlog #3 still
  blocked — 0 CHF salary rows; all 66 disclosed are EUR), trend logic (sound), the defensive CSV read
  (kept), or the dedup formula. Backlog status updates: #4 (Junior coverage) largely addressed —
  Junior n=46 / Intern n=59 (was n=1 early); #7 (discovery resilience under egress block) confirmed
  STILL the top operational risk — no allowlist change attempted (out of scope for this additive audit).
- **2026-06-25** (self-improvement meta-run on Opus): audited analysis_gen.py, LEARNINGS.md,
  jobs.csv (228 rows, 0 ragged, 0 empty job_id), reports/2026-06-24.md, skills_by_level.md.
  Confirmed `python3 analysis_gen.py 2026-06-25` runs clean (EXIT 0, N=228, new=10) before and
  after changes; also re-verified on RUN=1900-01-01 (prev=0 first-run path) and RUN=2026-06-27
  (future) — all three deliverables generate on every path. Two additive, verified changes to
  `analysis_gen.py`; **jobs.csv and its schema untouched**:
  (1) **Generic case-fold canonicalization** (backlog #8). Added `_build_case_map()`/`_CASE_MAP`:
  for every lowercased skill token, fold to its most-frequent casing in the dataset, applied after
  explicit `_SKILL_ALIASES`. Fixes ~48 case-only splits the hand map missed — e.g. `pandas` 8+5→12,
  `MLflow` 12+1→13(canon MLflow), `Computer Vision` 9+2+1→12, `data pipelines` 5+11+2→18,
  `machine learning`→`Machine Learning`, `Kubeflow`/`KubeFlow`, `ElasticSearch`/`Elasticsearch`,
  `FFmpeg`/`ffmpeg`. Verified via canon() that distinct compounds survive: `Azure OpenAI`, `RAG` vs
  `GraphRAG`, `Spark`/`PySpark`/`SparkML`, `Torch Distributor`/`torch.distributed`, `LLM Fine-Tuning`.
  (2) **Slashed-location country resolution** (backlog #6, analysis side). `country()` now maps
  comma-less slashed multi-city strings via a curated UNAMBIGUOUS DACH `_CITY_COUNTRY` table, applied
  only when the location has no comma and contains "/". Country mix cleaned from
  `{Germany 118, CH 51, AT 55, Munich/Berlin 2, Zurich/London 1, Heidelberg/Berlin 1}` →
  `{Germany 121, Switzerland 52, Austria 55}`. Unrecognised slashed strings fall through to prior
  behaviour (skip-if-unsure preserved). Both changes are read-time only; CSV not rewritten.
  Did NOT change: salary/FX logic (backlog #3 still blocked on no CH data), trend logic (sound),
  the defensive CSV read (kept), or the dedup formula. Egress-block on arbeitnow/datacareer/
  karriere (backlog #7) confirmed still the top operational risk — proxy status checked, no
  allowlist change attempted (out of scope for this additive audit).
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
