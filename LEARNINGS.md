# LEARNINGS — persistent skill memory for the DACH job-intelligence agent

Accumulated across runs. Append/update; do not delete history without reason.
Last audited: 2026-07-06 (self-improvement meta-run on Opus).

## Data quality issues observed (2026-07-06 audit)
- **Database stats:** **769 rows** (was 714 at the 2026-07-05 audit; **+55 from the 2026-07-05
  discovery run — 55 rows dated 2026-07-05**, added after that audit's 714-row snapshot), **0 ragged
  rows** (22 columns on every row), **0 empty `job_id`**, **0 duplicate `job_id`**, **0 rows with extra
  (None-key) columns**. `first_seen_date` distribution: `{2026-06-22: 16, 2026-06-23: 139, 2026-06-24: 27,
  2026-06-25: 80, 2026-06-26: 58, 2026-06-27: 87, 2026-06-28: 17, 2026-06-29: 52, 2026-06-30: 116,
  2026-07-01: 55, 2026-07-02: 32, 2026-07-03: 24, 2026-07-04: 11, 2026-07-05: 55}`. **No rows dated
  2026-07-06** yet (discovery agents run in parallel and may add 07-06 rows later), so with
  `RUN=2026-07-06` the genuine "new this run" count is **0** (all 769 rows fall into `prev`) and the
  report correctly renders the empty-run guard note. Country mix `{Germany 427, Switzerland 188,
  Austria 154}` (clean DACH-only, no leftover buckets); N=769 accounts fully.
- **Confirmed clean run status:** `python3 analysis_gen.py 2026-07-06` runs clean (EXIT 0, N=769,
  new=0). Re-verified on `RUN=1900-01-01` (prev=0 first-run path) — EXIT 0, all three deliverables
  generate (scratch `reports/1900-01-01.md` removed after testing).
- **✅ Prior-run regressions confirmed ALREADY REPAIRED in committed HEAD.** The 2026-07-05 audit
  escalated that committed HEAD `d9123a2` had dropped `_split_skills`/`ast`, the `natural language
  processing→NLP` + `golang→Go` folds, and the §4 tie-break, and had added a contradictory
  `data warehousing→Data Warehouse` fold. All are now correct in the working tree: `_split_skills()`
  with `ast.literal_eval` present (0 residual list-repr tokens after `canon()`), `natural language
  processing→NLP` (NLP=98) and `golang→Go` (Go=10, Golang=0) folds present, §4 tie-break
  `dist.sort(key=lambda x:(-x[3], x[0]))` present, and the data-warehousing fold reverted (git shows
  `1e1598f` added it, `f2f4173` "Revert contradictory data warehousing fold" removed it). Nothing to
  repair this run.
- **Skill-alias audit (strict n≥3-for-BOTH-forms bar, at N=769):** swept every `required_skills` /
  `nice_to_have_skills` token, aggressive-normalized (strip case + punctuation/spacing), and re-ran the
  full `canon()` pipeline — **0 residual case splits, 0 residual list-repr tokens** (the generic
  `_CASE_MAP` + explicit aliases absorb every case-only pair, e.g. pandas/Pandas 36/24,
  MLflow/MLFlow 55/3, machine learning→Machine Learning 88→201). **Every cross-form cluster clearing
  the n≥3-both-forms bar is a STANDING KEEP-SPLIT**: `GCP Vertex AI`(4)/`Vertex AI`(6) (sub-service
  rule, flagged for reconsideration), `data analysis`(27)/`data analytics`(3), `Speech Recognition`(3)/
  `Speech-to-Text`(3), `Multimodal AI`(3)/`multimodal models`(6), `REST API`(5)/`REST APIs`(12), and the
  `C++`(34)/`C#`(7) different-languages false-positive (norm collision). `Data Warehouse`(4)/
  `Data Warehousing`(**now 0**) no longer even clears the bar. Per respect-standing-decisions +
  skip-if-unsure, **the correct action is NO new fold.**
- **Why NO code change was made this run (deliberate skip, "if warranted" not met):** (1) the robustness
  features flagged as regressed on 2026-07-05 are already restored in HEAD; (2) the only cross-form
  alias candidates at the strict bar are standing keep-splits → correct action = no new fold; (3) all
  other output/salary/location logic verified clean and unchanged. Making a change with nothing
  warranted would violate additive-only / skip-if-unsure. `jobs.csv`, its schema, and the dedup formula
  were untouched.
- **Salary/country logic unchanged and clean:** **123 rows disclose pay (12 CHF)**; `country()` /
  `_CITY_COUNTRY`, AT-monthly ×14, CHF→EUR pinned 1.05, hourly ×40×52 all still render correctly. No new
  city/location issues (all 769 locations resolve to a DACH country).
- **Backlog status:** #9 (list-repr) recovery is INTACT again — `_split_skills` restored, 0 residual
  list-repr tokens; extraction side stays OPEN (legacy list-repr cells still transparently recovered).
  #7 (discovery resilience under egress block) remains the top operational risk. #1, #3, #5, #8, #10 all
  DONE and present in HEAD (previously-noted 07-05 regressions of #10 and part of #1 are resolved).

## Data quality issues observed (2026-07-05 audit)
- **Database stats:** **714 rows** (was 703 at the 2026-07-04 audit; **+11 from discovery runs since
  then — 11 rows dated 2026-07-04**, added after that audit's 703-row snapshot), **0 ragged rows** (22
  columns on every row), **0 empty `job_id`**, **0 duplicate `job_id`**, **0 rows with extra (None-key)
  columns**. `first_seen_date` distribution: `{2026-06-22: 16, 2026-06-23: 139, 2026-06-24: 27,
  2026-06-25: 80, 2026-06-26: 58, 2026-06-27: 87, 2026-06-28: 17, 2026-06-29: 52, 2026-06-30: 116,
  2026-07-01: 55, 2026-07-02: 32, 2026-07-03: 24, 2026-07-04: 11}`. **No rows dated 2026-07-05** yet
  (discovery agents run in parallel and may add 07-05 rows later), so with `RUN=2026-07-05` the genuine
  "new this run" count is **0** (all 714 rows fall into `prev`) and the report correctly renders the
  empty-run guard note. Country mix `{Germany 401, Switzerland 179, Austria 134}` (clean DACH-only);
  role mix `{Data Scientist 227, ML Engineer 182, AI Engineer 129, Data Engineer 105, AI Researcher 69,
  Other 2}`; seniority mix `{Mid 216, Senior 204, Intern 160, Junior 105, Lead/Principal 29}` — all
  values valid.
- **Confirmed clean run status:** `python3 analysis_gen.py 2026-07-05` runs clean (EXIT 0, N=714,
  new=0). Re-verified on `RUN=1900-01-01` (prev=0 first-run path) — EXIT 0, all three deliverables
  generate (scratch `reports/1900-01-01.md` removed after testing).
- **Skill-alias audit (strict n≥3-for-BOTH-forms bar, at N=714):** swept every `required_skills` /
  `nice_to_have_skills` token and aggressive-normalized (strip case + punctuation/spacing) to hunt
  cross-form splits. **The only n≥3-both-forms cross-form candidate this run was `Data Warehouse` vs
  `Data Warehousing`** (both-fields counts 4 / 3; required-only 2 / 2). **This pair is an EXPLICIT
  standing keep-split** — the 2026-07-04 audit considered it and deliberately left it split ("noun
  (tech) vs practice", same class as data analysis/analytics and Multimodal AI/multimodal models). Per
  "respect standing curated decisions" + skip-if-unsure, **the correct alias-dict action this run is NO
  new fold.** (The only aggressive-normalize collision found was `C++`/`C#` — the documented
  different-languages keep-split.)
- **⚠️ REGRESSION FOUND IN COMMITTED HEAD `d9123a2` — flagged for repair next run (NOT fixed this run;
  see rationale below):** the currently-committed `analysis_gen.py` is an OLDER base that has silently
  LOST three curated improvements documented in prior audits:
  - **Dropped `_split_skills()` + the `ast` import (the 2026-07-01 list-repr parser).** `sk()`/`nth()`/
    `_build_case_map()` are back to naive `.split(";")`. **54 rows (7.6% of the DB) store skills as a
    stringified Python list** (e.g. `['Python','PyTorch',...]`) and are now each collapsed into ONE bogus
    single token — so those 54 postings' real skills are **invisible to every table in
    `skills_by_level.md` (§1–§4)**. This is a MATERIAL degradation of the PRIMARY deliverable (backlog #9
    regressed from "recovered by `_split_skills`" to "mangled").
  - **Dropped `_SKILL_ALIASES` folds `natural language processing → NLP` (added 2026-07-03) and
    `golang → Go` (added 2026-07-04)** — both curated cross-form folds are absent from the committed map.
  - **Dropped the §4 deterministic secondary tie-break** (`dist.sort(key=lambda x:(-x[3], x[0]))`
    reverted to `key=lambda x:-x[3]`), reintroducing non-deterministic ordering of equal-gap skills.
  - **HEAD's commit message claims "…, LEARNINGS audit" but no 2026-07-05 LEARNINGS entry was actually
    written** (this entry fills that gap).
- **⚠️ The committed data-warehousing fold contradicts the 2026-07-04 keep-split.** HEAD `d9123a2` added
  `"data warehousing": "Data Warehouse"` to `_SKILL_ALIASES`, which reverses the explicit 2026-07-04
  decision to keep that pair split. Impact is **latent** (both forms sit below the top-15/20 table
  cutoffs, so no visible output-table change), but it is an unintended flip-flop of a one-day-old curated
  decision. **Recommend reverting it** alongside restoring the lost robustness above.
- **Why NO code change was made by this run (deliberate skip):** (1) the only strict-bar alias candidate
  is a standing keep-split → correct action = no new fold; (2) `analysis_gen.py` is being actively
  rewritten by a parallel meta-instance (the harness flagged the external edit as intentional and
  advised against reverting it), so in-race structural surgery risks clobbering/conflict; (3) restoring
  `_split_skills` + the two lost folds is a multi-point structural change, outside this run's
  "minimal additive change to the `_SKILL_ALIASES` dict" scope and the additive-only / one-change /
  skip-if-unsure rules. The disciplined action for an auditor finding a regression in code another
  process is actively editing is to **document + escalate**, which this entry (and the run's final
  report) does. `jobs.csv` and its schema were left untouched; the dedup formula was untouched.
- **Salary/country logic unchanged and clean:** **112 rows disclose pay (12 CHF)**; `country()` /
  `_CITY_COUNTRY`, AT-monthly ×14, CHF→EUR pinned 1.05, hourly ×40×52 all still render correctly.
- **Backlog status:** #9 (list-repr) **REGRESSED to OPEN-CRITICAL** — the `_split_skills` recovery was
  removed from committed HEAD; 54 list-repr rows currently mangled → **top repair priority for next
  run: restore `_split_skills`+`ast`, the `natural language processing→NLP` and `golang→Go` folds, and
  the §4 tie-break; and revert the contradictory data-warehousing fold**. #7 (discovery resilience under
  egress block) remains the top operational risk. #1, #3, #5, #8, #10 were DONE but #10 (tie-break) and
  part of #1 (NLP/golang folds) are regressed in committed HEAD as noted.

## Data quality issues observed (2026-07-04 audit)
- **Database stats:** **703 rows** (was 679 at the 2026-07-03 audit; **+24 from the 2026-07-03
  discovery run — 24 rows dated 2026-07-03**), **0 ragged rows** (22 columns on every row),
  **0 empty `job_id`**, **0 duplicate `job_id`**, **0 rows with extra (None-key) columns**.
  `first_seen_date` distribution: `{2026-06-22: 16, 2026-06-23: 139, 2026-06-24: 27, 2026-06-25: 80,
  2026-06-26: 58, 2026-06-27: 87, 2026-06-28: 17, 2026-06-29: 52, 2026-06-30: 116, 2026-07-01: 55,
  2026-07-02: 32, 2026-07-03: 24}`. **No rows dated 2026-07-04**, so with `RUN=2026-07-04` the genuine
  "new this run" count is **0** (all 703 rows fall into `prev`), and the report correctly renders the
  empty-run guard note. Country mix `{Germany 393, Switzerland 177, Austria 133}` (clean DACH-only, no
  leftover buckets); role mix `{Data Scientist 225, ML Engineer 177, AI Engineer 126, Data Engineer 105,
  AI Researcher 68, Other 2}`; seniority mix `{Mid 212, Senior 202, Intern 156, Junior 104,
  Lead/Principal 29}` — all values valid. No-comma locations all still resolve (`Zurich/London`→CH,
  `Munich/Berlin`×2 / `Heidelberg/Berlin`→DE via `_CITY_COUNTRY`, bare `Germany`×10,
  `Germany (Remote)`×5 via the parenthetical strip).
- **Confirmed clean run status:** `python3 analysis_gen.py 2026-07-04` runs clean (EXIT 0, N=703,
  new=0) BEFORE and AFTER the change. Re-verified on `RUN=1900-01-01` (prev=0 first-run path) and
  `RUN=2026-07-02` (new=32) — all three deliverables generate on every path, EXIT 0 each. (The scratch
  `reports/1900-01-01.md` verification artifact was removed after testing.)
- **🛠️ One additive, verified change to `analysis_gen.py` (jobs.csv + schema untouched):**
  - **New `_SKILL_ALIASES` synonym fold `golang → Go` (backlog #1).** Swept all tokens at N=703 through
    the full `canon()` pipeline — **0 residual case splits, 0 residual list-repr tokens** (the generic
    `_CASE_MAP` + existing aliases still absorb everything case-only). The one clear cross-form split
    meeting the strict "n≥3 for BOTH forms" bar was `Golang`(3) vs the canonical `Go`(7) — the exact
    same programming language (`Golang` is merely the informal/search-friendly name for `Go`), same
    class as the existing `k8s→Kubernetes` / `recommendation systems→recommender systems` synonym folds.
    Folded the synonym to the more-frequent canonical → **`Go` (10)**. Full-token only: the alias maps
    the exact token `golang` and can never touch `Go` itself or substrings (e.g. MongoDB). Latent merge
    (Go 10 sits below the top-15/20 table cutoffs) — no output-table regression this run.
- **Considered but NOT folded (deferred to standing curated decisions / skip-if-unsure):**
  - **`GCP Vertex AI`(4) vs `Vertex AI`(6)** — both now clear the n≥3-both-forms bar, same GCP product,
    and folding would mirror the existing vendor-prefix `amazon/aws sagemaker → SageMaker` precedent.
    HOWEVER there is an **explicit, repeated prior curated decision** (2026-06-28 / 2026-07-03 audits) to
    keep these split under the "GCP/Azure sub-service rule." Rather than reverse a standing decision in an
    additive audit, LEFT SPLIT and flagged here as a candidate for reconsideration next run (the SageMaker
    inconsistency is real: `Vertex AI` is a standalone product like SageMaker, not a distinct offering like
    `Azure OpenAI`). Skip-if-unsure applied.
  - **`data analysis`(23)/`data analytics`(3)** — analysis vs analytics is a genuine word-form/scope
    distinction (act vs discipline/BI); left split. **`Speech Recognition`(3)/`Speech-to-Text`(3)** —
    both exactly at threshold, close but with semantic room; left split. **`Data Warehouse`(4)/`Data
    Warehousing`(3)** — noun (tech) vs practice; left split. **`Multimodal AI`(3)/`multimodal models`(6)**
    — differ by AI-field vs model-artifacts; left split. **`MLOps`(65)/`ML Ops`(1)**, **`AI Automation`(3)/
    `AI/ML`(3)** (distinct concepts), **`C++`(32)/`C#`(7)** (different languages), **`REST API`(5)/`REST
    APIs`(12)** (deliberate singular/plural split) — all left split per prior decisions.
- **`_CITY_COUNTRY` / `country()` verified complete; salary logic clean (no change).** All locations
  resolve to a DACH country; **112 rows disclose pay (12 CHF)**; AT-monthly ×14, CHF→EUR pinned 1.05,
  hourly ×40×52 all render correctly. No new city entries, no FX change.
- **Extraction quality holding:** all **24 new 2026-07-03 rows store skills as semicolon-separated
  strings — 0 list-repr cells among them** (extraction side stays clean, trend continues from 06-30).
  **108 legacy list-repr cells remain** in older DB rows, all transparently recovered by `_split_skills`
  (backlog #9 extraction-side stays OPEN but stable).
- **Backlog status:** #1 still DONE (extended today with the `golang→Go` synonym fold); #1b, #6
  (extraction side), #7 (discovery resilience under egress block — **TOP operational risk**, all 3
  primary boards arbeitnow/datacareer/karriere still presumed proxy-blocked; the 24 new rows came from
  WebSearch + ATS/career pages), #9 (108 legacy list-repr cells) all STILL OPEN. #3, #5, #8, #10 remain DONE.

## Data quality issues observed (2026-07-03 audit)
- **Database stats:** **679 rows** (unchanged since the 2026-07-02 audit; **no discovery run has
  written rows dated 2026-07-03**), **0 ragged rows** (22 columns on every row), **0 empty `job_id`**,
  **0 duplicate `job_id`**, **0 rows with extra (None-key) columns**. `first_seen_date` distribution
  unchanged: `{2026-06-22: 16, 2026-06-23: 139, 2026-06-24: 27, 2026-06-25: 80, 2026-06-26: 58,
  2026-06-27: 87, 2026-06-28: 17, 2026-06-29: 52, 2026-06-30: 116, 2026-07-01: 55, 2026-07-02: 32}`.
  With `RUN=2026-07-03` the genuine "new this run" count is **0** (all 679 rows fall into `prev`), so
  the report correctly renders the empty-run guard note. Country mix `{Germany 379, Switzerland 169,
  Austria 131}` (clean DACH-only, no leftover buckets); no-comma locations all still resolve
  (`Zurich/London`→CH, `Munich/Berlin`×2 / `Heidelberg/Berlin`→DE via `_CITY_COUNTRY`, bare `Germany`
  ×10, `Germany (Remote)`×5 via the parenthetical strip).
- **Confirmed clean run status:** `python3 analysis_gen.py 2026-07-03` runs clean (EXIT 0, N=679,
  new=0) BEFORE and AFTER the change. Re-verified on `RUN=1900-01-01` (prev=0 first-run path),
  `RUN=2026-07-02` (new=32) and `RUN=2026-07-01` (new=55) — all three deliverables generate on every
  path, EXIT 0 each. (The scratch `reports/1900-01-01.md` verification artifact was removed after
  testing.)
- **🛠️ One additive, verified change to `analysis_gen.py` (jobs.csv + schema untouched):**
  - **New `_SKILL_ALIASES` acronym fold `natural language processing → NLP` (backlog #1).** Swept all
    tokens at N=679 through the full `canon()` pipeline — **0 residual case splits, 0 residual
    list-repr tokens** (the generic `_CASE_MAP` + existing aliases still absorb everything case-only).
    The one genuine cross-form split meeting the "n≥3 for BOTH forms" bar was `Natural Language
    Processing`(12) vs the dominant acronym `NLP`(77) — identical concept, same class as the existing
    `large language models→LLMs` / `genai→Generative AI` acronym folds. Folded the long form to the
    acronym → **`NLP` (89)**. Full-token only: verified the distinct compounds `medical NLP`,
    `NLP Transformers`, `NLP publications`, `NLP project experience` (all n=1) survive unchanged. This
    fold DOES move the §1 top-skills table (NLP climbs 77→89), a correct de-duplication, not noise.
- **No other aliases warranted (strict n≥3-both-forms bar).** The remaining punctuation/word-form
  near-dup clusters at N=679 all fail the bar and are left split per skip-if-unsure: `MLOps`(64)/
  `ML Ops`(1), `AI Automation`(3)/`AI/Automation`(1), `Multimodal AI`(3)/`multi-modal AI`(1) — second
  form n=1 each; `C++`(32)/`C#`(7) are different languages (never merge); `REST API`(5)/`REST APIs`(12)
  are deliberately kept split by the existing `restful api`/`restful apis` aliases (singular/plural
  decision preserved). `GCP Vertex AI`(4)/`Vertex AI`(6) stay distinct per the sub-service rule.
- **`_CITY_COUNTRY` / `country()` verified complete; salary logic clean (no change).** All locations
  resolve to a DACH country; AT-monthly ×14, CHF→EUR pinned 1.05, hourly ×40×52 all render correctly.
  No new city entries, no FX change.
- **Backlog status:** #1 still DONE (extended today with the NLP acronym fold); #1b, #6 (extraction
  side), #7 (discovery resilience under egress block — TOP operational risk, all 3 primary boards
  still presumed proxy-blocked), #9 (extraction should emit `";".join(skills)` — 108 legacy list-repr
  cells remain, all recovered by `_split_skills`) all STILL OPEN. #3, #5, #8, #10 remain DONE.

## Data quality issues observed (2026-07-02 audit)
- **Database stats:** **679 rows** (was 592 at the 2026-07-01 audit; **+87 across the 2026-07-01
  and 2026-07-02 discovery runs — 55 dated 2026-07-01, 32 dated 2026-07-02**), **0 ragged rows**
  (22 columns on every row), **0 empty `job_id`**, **0 duplicate `job_id`**, **0 rows with extra
  (None-key) columns**. `first_seen_date` distribution: `{2026-06-22: 16, 2026-06-23: 139,
  2026-06-24: 27, 2026-06-25: 80, 2026-06-26: 58, 2026-06-27: 87, 2026-06-28: 17, 2026-06-29: 52,
  2026-06-30: 116, 2026-07-01: 55, 2026-07-02: 32}`. With `RUN=2026-07-02` the genuine "new this
  run" count is **32** (matches the swarm consolidation: DE=15, CH=10, AT=7; roles ML Eng=10,
  DS=9, AI Res=6, AI Eng=6, Data Eng=1; seniority Intern=15, Junior=7, Mid=6, Senior=3, Lead=1).
  Full-DB seniority mix now `{Mid 209, Senior 196, Intern 147, Junior 100, Lead/Principal 27}` —
  all values valid (Intern/Junior/Mid/Senior/Lead/Principal). Consolidation reported 86 job_ids
  skipped as existing dups + 2 batch-internal dups; the 0-duplicate DB confirms dedup held.
- **Confirmed clean run status:** `python3 analysis_gen.py 2026-07-02` runs clean (EXIT 0, N=679,
  new=32) BEFORE and AFTER the changes. Re-verified on the real files at `RUN=1900-01-01` (prev=0
  first-run path) and `RUN=2026-07-01` (new=55) — all three deliverables generate on every path,
  EXIT 0 each. skills_by_level.md, salary_benchmarks.md and reports/2026-07-02.md are **byte-identical
  before/after both edits** (the folded tokens sit below the top-N table cutoffs and no equal-gap
  §4 tie reordered this run) — pure additive changes with zero output regression.
- **New rows are format-clean (extraction quality improving).** All 32 new rows store skills as
  **semicolon-separated strings — 0 list-repr (`['Python', …]`) cells among them** (vs 54/116 on
  2026-06-30). All 32 locations are proper `"City, Country"` (Gland/Lausanne/Zurich/Basel/Geneva CH,
  Vienna/Villach/Premstätten AT, Munich/Berlin/Hamburg/Frankfurt/etc. DE) — `country()` resolves
  every one, no slashed/parenthetical specials this run. NOTE: **108 list-repr cells remain in the
  older DB rows**, still transparently recovered by the hardened `_split_skills()` net (backlog #9
  extraction-side stays OPEN, but the newest scraper output is clean — trend is in the right direction).
- **🛠️ Two additive, verified changes to `analysis_gen.py` (jobs.csv + schema untouched):**
  - **(1) Two new `_SKILL_ALIASES` synonym/spacing folds (backlog #1).** Swept all tokens at N=679
    through the full `canon()` pipeline — **0 residual case splits, 0 residual list-repr tokens** (the
    generic `_CASE_MAP` + existing aliases still absorb everything case-only). Two genuine cross-form
    splits surfaced that the case-fold cannot bridge (differ by word-form / hyphen, not just case):
    `recommendation systems`(5) + `recommender systems`(9) → **`recommender systems` (14)**, and
    `Vision-Language Models`(1) + `vision language models`(3) → **`vision language models` (4)**. Both
    are full-token folds (mirror the existing time-series / infrastructure-as-code / ms-sql curated
    folds). Verified distinct compounds survive: `real-time recommender systems` (1) and
    `Vision Transformers` (3) unchanged. No output-table change (both below the top-15/20 cutoffs) —
    the merge is latent until either token climbs into a ranked table.
  - **(2) Deterministic §4 tie-break (backlog #10, now DONE).** §4 "What gets added as you go up"
    iterates a `set()` and previously sorted by gap ALONE (`key=lambda x:-x[3]`), so equal-gap skills
    (e.g. LangChain vs Hugging Face, both +4) swapped order non-deterministically between runs —
    harmless (counts identical) but noisy in diffs. Changed to `key=lambda x:(-x[3], x[0])` (gap desc,
    then skill name asc). No value/membership change, only stable ordering; output byte-identical this
    run (no top-15 tie happened to reorder). Closes the last logged low-priority code-hygiene item.
- **`_CITY_COUNTRY` / `country()` verified complete.** All 32 new locations carry a comma and resolve
  via the last-segment path; the map needed no new entries. Country mix full-DB stays clean DACH-only.
- **Salary logic clean (no change).** AT-monthly ×14, CHF→EUR pinned 1.05, hourly ×40×52 all render
  correctly; the new CH rows (Gland/Lausanne/Zurich/Basel/Geneva) that disclose pay flow through
  `to_eur()` with the `~EUR-eq` column. No anomalies.
- **Backlog status updates:**
  - **#1** (read-time skill canonicalization) — still DONE; extended today with 2 synonym/spacing
    folds. **#1b** (extraction emits canonical spellings) — STILL OPEN; `canon()` neutralises impact.
  - **#9** (extraction must emit `";".join(skills)`, not `str(list)`) — STILL OPEN, but **improving**:
    0/32 new rows used list-repr this run (108 legacy cells remain, all recovered by `_split_skills`).
  - **#10** (deterministic §4 tie-break) — **DONE this run** (see change 2 above).
  - **#7** (discovery resilience under egress block) — STILL OPEN / top operational risk. All primary
    boards (arbeitnow, datacareer.ch, karriere.at) remain proxy-blocked; all 120 discovered / 32 kept
    jobs came from WebSearch + ATS/career pages (greenhouse.io, ashbyhq.com, smartrecruiters,
    bmwgroup.jobs, etc.). WebSearch → career-page/ATS remains the only viable channel.
  - **#6** (extraction stores `"City, Country"`) — analysis side DONE; extraction side effectively
    honoured this run (all 32 new locations already `"City, Country"`), map unchanged.

## Data quality issues observed (2026-07-01 audit)
- **Database stats:** **592 rows** (unchanged since the 2026-06-30 audit; **no discovery run has
  written rows dated 2026-07-01**), **0 ragged rows**, **0 empty `job_id`**, **0 duplicate `job_id`**,
  **0 rows with extra (None-key) columns**, 22 columns on every row. `first_seen_date` distribution
  is unchanged: `{2026-06-22: 16, 2026-06-23: 139, 2026-06-24: 27, 2026-06-25: 80, 2026-06-26: 58,
  2026-06-27: 87, 2026-06-28: 17, 2026-06-29: 52, 2026-06-30: 116}`. With `RUN=2026-07-01` the genuine
  "new this run" count is **0** (all 592 rows fall into `prev`), so the report correctly renders the
  empty-run guard note. Country mix DE=331, CH=145, AT=116; role mix DS=190, ML Eng=141, AI Eng=108,
  Data Eng=92, AI Res=59, Other=2; seniority Mid=183, Senior=180, Intern=118, Junior=85, Lead=26.
- **Confirmed clean run status:** `python3 analysis_gen.py 2026-07-01` runs clean (EXIT 0, N=592,
  new=0) BEFORE and AFTER the change. Re-verified on the real files at `RUN=1900-01-01` (prev=0
  first-run path) and `RUN=2026-06-30` (new=116) — all three deliverables generate on every path,
  EXIT 0 each. skills_by_level.md and salary_benchmarks.md are byte-identical before/after the edit
  (the only textual delta is a non-deterministic LangChain/Hugging Face row swap in §4 — see below —
  which is pre-existing and unrelated to the edit).
- **🛠️ Safe additive hardening applied to `_split_skills` (list-repr parser).** The 2026-06-30 fix
  detected a stringified-Python-list skill cell with the guard `startswith("[") and endswith("]") and
  ";" not in field`. That `";" not in field` guard has a latent hole: a list-repr can legitimately
  carry a `;` INSIDE a quoted element (e.g. `"['Python', 'CI/CD; testing', 'PyTorch']"`), in which
  case the old code mis-routed the whole cell into the naive `;`-split and shredded the tokens.
  **Change (2026-07-01):** try `ast.literal_eval` FIRST on ANY `"[...]"` cell; use the result only if
  it yields a list/tuple, otherwise fall back to the exact prior `;`-split. **Verified byte-for-byte
  identical to prior behaviour on all 592 current rows (0 differing cells)** — no count changes; this
  is pure future-proofing of the same bug class. A non-list `"[...]"` string still falls through
  unchanged. jobs.csv NOT modified — read-time only.
- **No new skill aliases warranted (pipeline already complete for all live data).** Swept every skill
  token at N=592. AFTER the full `canon()` pipeline there are **0 residual case splits and 0 residual
  list-repr tokens** — the generic `_CASE_MAP` (most-frequent-casing fold) already absorbs all ~95
  case-only pairs seen (pandas/Pandas, MLflow/MLFlow, data pipelines/Data Pipelines, deep learning/
  Deep Learning, etc.), and the explicit `_SKILL_ALIASES` handle the punctuation/vendor-prefix splits.
  Spot-checked candidates: `Infrastructure-as-Code`/`infrastructure-as-code`/`Infrastructure as Code`
  all fold to `Infrastructure as Code`; `MS-SQL`/`MS SQL` fold; all `time series analysis` casings fold
  to `Time Series Forecasting`. The only remaining multi-spelling clusters are n=1–2 genuinely-distinct
  or borderline hyphen pairs that must NOT auto-merge: `Vision-Language Models`/`Vision Language Models`
  (n=1 each), `AI/Automation`/`AI Automation` (n=1/2), `C++`/`C#` (different languages) — left split
  per skip-if-unsure. No `_SKILL_ALIASES` or `_CITY_COUNTRY` additions needed.
- **`_CITY_COUNTRY` map verified complete for all live locations.** The only no-comma locations in the
  DB are `Germany` (8), `Germany (Remote)` (5, stripped by the parenthetical guard), `Munich/Berlin`
  (2→Germany), `Zurich/London` (1→Switzerland), `Heidelberg/Berlin` (1→Germany) — all resolve to the
  correct DACH country. No new city entries needed.
- **Salary logic clean.** 105 of 592 rows disclose pay. AT-monthly ×14, CHF→EUR at pinned 1.05, and
  hourly ×40×52 all render correctly; CHF rows (Anthropic, Novartis, comparis.ch, CERN, PEAX, BLP,
  Ergon) carry the `~EUR-eq` column. No anomalies, no code change.
- **Backlog status updates:**
  - **#1b** (extraction emits canonical skill spellings) — STILL OPEN. Read-time `canon()` fully
    neutralises the impact for now; the analysis side needs nothing further.
  - **#6** (extraction stores `"City, Country"`) — analysis side DONE; extraction side STILL OPEN but
    zero live locations are currently unresolved, so no analysis impact.
  - **#7** (discovery resilience under egress block) — STILL OPEN / top operational risk. No discovery
    ran on 2026-07-01 (0 new rows). WebSearch → career-page/ATS remains the working path; primary boards
    (arbeitnow, datacareer.ch, karriere.at) presumed still proxy-blocked.
  - **#9** (extraction must emit `";".join(skills)`, not `str(list)`) — STILL OPEN, HIGH PRIORITY. The
    read-time `_split_skills` safety net (now hardened) keeps counts correct, but the source scrapers /
    `consolidate.py` should still write semicolon-separated skills so jobs.csv is self-describing.
  - **NEW #10 (logged, NOT implemented — low priority):** §4 "What gets added as you go up" iterates a
    `set()` and sorts only by gap, so equal-gap skills (e.g. LangChain vs Hugging Face, both +4) swap
    order non-deterministically between runs. Harmless (counts identical) but makes diffs noisy. Safe
    future fix: add a deterministic secondary tie-break to the `dist.sort` key (e.g. `-gap, skill`).
    Left for a future run to avoid touching the ranking sort outside today's scope.

## Data quality issues observed (2026-06-30 audit)
- **Database stats:** **592 rows** (was 476 at the 2026-06-29 audit; **+116 this run**), **0 ragged
  rows**, **0 empty `job_id`**, **0 duplicate `job_id`**. `first_seen_date` distribution:
  `{2026-06-22: 16, 2026-06-23: 139, 2026-06-24: 27, 2026-06-25: 80, 2026-06-26: 58, 2026-06-27: 87,
  2026-06-28: 17, 2026-06-29: 52, 2026-06-30: 116}`. With `RUN=2026-06-30` the genuine "new this run"
  count is **116** (country DE=75, CH=24, AT=17 after `country()` resolution; roles DS=38, ML Eng=32,
  Data Eng=17, AI Eng=15, AI Res=14; seniority Mid=41, Senior=39, Intern=17, Junior=16, Lead=3).
  `python3 analysis_gen.py 2026-06-30` runs clean (EXIT 0, N=592, new=116) BEFORE and AFTER the change;
  re-verified in a scratch copy on RUN=1900-01-01 (prev=0 first-run path) and RUN=2026-06-29 — all
  three deliverables generate on every path.
- **🚨 NEW data-quality bug found & FIXED (read-time, additive): list-repr skill cells.** **54 of the
  116 new rows (47%)** stored `required_skills`/`nice_to_have_skills` as a **stringified Python list**,
  e.g. `"['Python', 'PyTorch', 'Deep Learning']"` (NO semicolons), instead of the spec's
  semicolon-separated format. The whole run came from the scratchpad `consolidate.py` / per-source
  JSON files (jobs_germany.json, jobs_switzerland.json, jobs_banks.json, jobs_ai_native.json, …), and
  roughly half of those sources serialized the skill list with Python `repr()` rather than
  `";".join(...)`. **Impact before the fix:** `analysis_gen.py` `sk()`/`nth()` split ONLY on `;`, so
  each `[...]` blob counted as ONE bogus skill token — every skill in those 54 rows was INVISIBLE to
  the skills-by-level analysis (a silent thin result, violating the "never silently produce a thin run"
  rule). Affected big names: Aleph Alpha, Helsing, Black Forest Labs, BMW, Siemens, SAP, Bosch,
  Mercedes-Benz, Canva, Red Bull, Delivery Hero, Scalable Capital, N26, Sportradar.
  **Fix:** added `_split_skills(field)` — if a cell starts `[`, ends `]`, and has no `;`, it is parsed
  via `ast.literal_eval` into its elements; everything else falls through to the exact prior `;`-split
  (so well-formed rows are byte-for-byte unchanged). Wired into `sk()`, `nth()`, AND `_build_case_map()`
  so the case-vote also sees the recovered tokens. After the fix: 0 residual `[...]` tokens; `Python`
  jumped to 536, `Machine Learning` 206, `PyTorch` 164 (was undercounting by ~54 each). jobs.csv NOT
  modified — read-time safety net only. **Extraction-side fix REQUIRED:** `consolidate.py` and every
  per-source scraper must emit skills as `";".join(skills)` (CSV-safe), never `str(list)` — see new
  backlog #9. This is the same class as backlog #1b (extraction should write canonical tokens) but more
  urgent because it silently zeroes whole rows, not just splits counts.
- **CHF salary data confirmed and growing.** 11 CHF salary rows now in the DB (was 9 at 2026-06-29).
  New CHF rows this run: CERN Geneva (two monthly bands 5266–5793 and 6372–7004 CHF/month) and
  **Novartis Basel 102k–190k CHF/yr**. `to_eur()` (pinned 1 CHF = 1.05 EUR) converts them correctly in
  both the disclosed-salaries table and the by-role EUR median pool (e.g. Novartis ~146k CHF → ~153k EUR,
  CERN 6372–7004/mo → ~80k CHF → ~84k EUR at ×12). No code change needed — the 2026-06-29 CHF path
  handles the new rows. New EUR-disclosing rows this run: 10 (mix of AT-monthly and DE/AT-yearly).
- **Discovery: 100% company-career-page / ATS this run; all primary public boards still blocked.**
  All 116 jobs came from WebSearch → direct career pages / ATS hosts (arbeitnow/datacareer/karriere
  remain proxy-blocked in cloud — unchanged). **Sources confirmed working today** (add to rotation):
  greenhouse.io / Greenhouse ATS (Black Forest Labs, others), ashbyhq.com / Ashby ATS (Aleph Alpha),
  Helsing direct careers, jobs.smartrecruiters.com / SmartRecruiters (incl. Bosch), join.com (6 jobs),
  bmwgroup.jobs (BMW), jobs.siemens.com + Siemens/Siemens-Energy Careers Marketplace, jobs.sap.com /
  SAP Careers (heavy contributor, ~8 rows), jobs.mercedes-benz.com, jobs.check24.de (CHECK24),
  careers.deliveryhero.com (Delivery Hero), jobs.redbull.com (Red Bull), lifeatcanva.com (Canva),
  jobs.anton-paar.com, careers.andritz.com, careers.greentube.com, devjobs.at, createyourowncareer.com,
  N26 careers page. New companies seen today also include: REWE International, Sportradar, A1 Telekom
  Austria, Machine Learning Reply, EnliteAI, Themisphere, FREENOW, Buynomics, Bertelsmann, Synthflow AI,
  WeSort.AI, Datasphere Analytics, Greentube, Boehringer Ingelheim, Raiffeisen Bank International.
- **Minor residual skill near-dups (left split, n=1, per skip-if-unsure):** after `canon()` the only
  remaining multi-spelling clusters at N=592 are genuine distinct or single-occurrence pairs that must
  NOT auto-merge: `C++`/`C#` (different languages — never merge), `AI Automation`/`AI/Automation` (n=1),
  `Multimodal AI`/`multi-modal AI` (n=1), `Vision-Language Models`/`Vision Language Models` (n=1 each,
  hyphen-only — borderline but left split, too rare to matter). No new `_SKILL_ALIASES` entries
  warranted this run. NOTE: the recovered list-repr tokens fold cleanly through the existing aliases +
  `_CASE_MAP` (e.g. `data pipelines`, `statistics`, `matplotlib`, `distributed systems` all case-fold).

## Data quality issues observed (2026-06-29 audit)
- **Database stats:** **476 rows** (was 407 at the 2026-06-28 audit; +69 across the 2026-06-28
  and 2026-06-29 discovery runs). With `RUN=2026-06-29` the genuine "new this run" count is **52**
  (DE=28, CH=14, AT=10; roles DS=21, AI Eng=9, ML Eng=9, AI Res=8, Data Eng=5; seniority
  Senior=15, Mid=17, Intern=15, Junior=4, Lead=1). `python3 analysis_gen.py 2026-06-29` runs clean
  (EXIT 0, N=476, new=52) BEFORE and AFTER the changes; re-verified in a scratch copy on
  RUN=1900-01-01 (prev=0 first-run path) and RUN=2026-06-28 (new=17) — all three deliverables
  generate on every path.
- **CHF salary data is now CONFIRMED in the DB — backlog #3 unblocked and IMPLEMENTED.** Switzerland
  formerly disclosed no salary; it now does. CHF rows present: Anthropic Zurich 280k–680k CHF/yr,
  Novartis Basel 102k–190k CHF/yr (prior runs), comparis.ch Zurich 90k–120k CHF/yr, BLP Digital
  110k–140k CHF/yr, PEAX 140k–180k CHF/yr, Ergon 55k–70k CHF/yr, plus CHF **monthly** rows: CERN
  Geneva ML Eng 5266–5793 CHF/month, CERN Geneva DS 6372–7004 CHF/month, and the new-today CERN
  Meyrin studentship **3486 CHF/month**. `analysis_gen.py` now converts CHF→EUR at a pinned
  **1 CHF = 1.05 EUR** rate (`CHF_TO_EUR`, `to_eur()`): the disclosed-salaries table keeps the
  original currency/values and adds a new "~Annualised (EUR-eq)" column, and the by-role median pool
  now includes CHF rows converted to EUR (was EUR-only). Re-check the pinned rate quarterly.
- **New EUR/hour salary occurrence:** deeplify (Munich) Working Student ML at **28–35 EUR/hour**
  (annualises ×40×52 → ~66k). Other EUR/hour rows: FREQUENTUM 16–18, KOSTAL 13–15, Delicious Data
  20–25, CARIAD 12.82–17.80. Hourly handling in `annual()` unchanged (×40×52).
- **NEW skill-alias decision: collapse time-series phrasings to ONE canonical.** Raw data carried 5
  split spellings — `Time Series Forecasting`, `time series forecasting`, `Time Series Analysis`,
  `Time series analysis`, `time series analysis` (seen e.g. in Siemens/ZEISS postings, which use the
  terms interchangeably). Previously `analysis_gen.py` folded "analysis" → `Time Series Analysis` and
  "forecasting" → `Time Series Forecasting` (two distinct canonicals, still splitting the count).
  **Changed 2026-06-29:** all four/five variants now fold to **`Time Series Forecasting`** (verified
  via `canon()`). Full-token fold, not substring — distinct compounds unaffected.
- **`Power BI` and `Machine Learning` casing already handled by the generic `_CASE_MAP`** — verified,
  no hand-alias needed. `Power BI`(25)/`PowerBI`(2)/`powerbi`(1) fold to `Power BI` (the explicit
  `powerbi→Power BI` alias plus the case-fold). `Machine Learning`(83)/`machine learning`(51) fold to
  `Machine Learning` via the explicit alias. Both confirmed correct at N=476.
- **First Lead/Principal row dated 2026-06-29:** Vestiaire Collective "Data Engineering Manager"
  (Berlin), explicitly a people-manager role leading a team — correctly assigned Lead/Principal.
- **job_id collision behavior re-confirmed (expected, per spec).** `job_id = hash(company +
  normalized_role + location)` intentionally collapses distinct postings that share those three.
  Today's examples: two Aleph Alpha AI Engineer roles (Heidelberg) → one row `79c97a376fde`; two BMW
  Group ML Engineer roles (Munich) → one row `8b5aa03ed4d5`; two Siemens AI Engineer roles (Munich) →
  one row `d448c993e614`. Only one row kept each; note the dropped role in the daily report so the
  count stays explainable.
- **Discovery via unblocked career-page hosts working well.** Primary boards (arbeitnow,
  datacareer.ch, karriere.at) remain proxy-blocked in cloud; today's 52 jobs came from WebSearch +
  direct/ATS career pages. NEW sources confirmed working this run (add to the unblocked-host
  rotation): Aleph Alpha (ashbyhq), Helsing (direct), Black Forest Labs (greenhouse),
  Google DeepMind Zurich (greenhouse), BMW Group (bmwgroup.jobs), Rohde & Schwarz (direct),
  CARIAD/VW (volkswagen-group.com), Continental (direct), Bosch (smartrecruiters),
  ZEISS (myworkdayjobs), NEURA Robotics (direct), CERN (smartrecruiters). Other new companies
  discovered today: Inceptive, Commerzbank, ING Germany, DATEV, Scalable Capital, QIMA, Brandback,
  Kineo, deeplify, Wingtra AG, Skydio, Mercedes-Benz.

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
- **Unblocked career-page / ATS hosts confirmed working (2026-06-29).** With the primary boards
  proxy-blocked, these channels delivered today's 52 jobs and should be the default rotation:
  WebSearch (discovery) → then fetch on: greenhouse.io (Anthropic, Black Forest Labs, Google
  DeepMind Zurich), ashbyhq.com (Aleph Alpha, BLP Digital), lever.co (Vestiaire Collective),
  join.com (deeplify, PEAX, Delicious Data), jobs.smartrecruiters.com (CERN, Bosch),
  myworkdayjobs.com (ZEISS), bmwgroup.jobs (BMW), volkswagen-group.com (CARIAD/VW), plus direct
  career pages for Helsing, Rohde & Schwarz, Continental, NEURA Robotics.
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
3. **CHF/EUR FX** — DONE (2026-06-29). CHF salary rows now exist (Anthropic, Novartis, comparis.ch,
   BLP, PEAX, Ergon, CERN ×3), so the conversion is implemented with a pinned, documented
   **1 CHF = 1.05 EUR** rate (`CHF_TO_EUR` / `to_eur()` in `analysis_gen.py`) — no live FX lookup, so
   runs stay reproducible. The disclosed-salaries table preserves the original currency/values and
   adds an EUR-equivalent column; the by-role median pool now includes CHF rows converted to EUR
   (was EUR-only). Re-check the pinned rate quarterly. Other currencies pass through `to_eur()` as
   `None` (excluded from the EUR pool, not mis-counted).
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
9. **Extraction must emit semicolon-separated skills, not `str(list)` (open, HIGH PRIORITY).**
   Found 2026-06-30: 54/116 new rows stored skills as a Python list-repr string
   (`"['Python', 'PyTorch', ...]"`) because `consolidate.py` / some per-source scrapers used
   `repr()`/`str(list)` instead of `";".join(skills)`. This silently zeroed those rows' skills in the
   analysis until the read-time `_split_skills()` safety net was added. **Fix at the source:** every
   scraper and `consolidate.py` must serialize `required_skills`/`nice_to_have_skills` as
   `";".join(canonical_skill_list)` (CSV-safe, escape any embedded `;`/`"`). Read-time parsing is the
   net; extraction-side is the real fix (mirrors backlog #1b). Until then, `analysis_gen.py` handles
   both formats transparently.
8. **Generic case-fold canonicalization** — DONE (2026-06-25). `analysis_gen.py` now derives, per
   lowercased skill token, the most-frequently-seen casing in the dataset and folds all other
   casings to it (`_build_case_map()` / `_CASE_MAP`), applied AFTER the explicit `_SKILL_ALIASES`
   so curated decisions win. Generalises the hand-added case entries to ALL case-only splits
   (~48 found at N=228). Cannot merge distinct skills (collapse requires byte-identical lowercased
   tokens). Extraction-time canonical casing (backlog #1b) remains the source-of-truth fix.

## Audit log
- **2026-07-06** (self-improvement meta-run on Opus): audited analysis_gen.py, LEARNINGS.md, jobs.csv
  (**769 rows, 0 ragged, 0 empty job_id, 0 duplicate job_id, 0 extra-column rows** — 22 cols every row;
  +55 vs the 714 at the 2026-07-05 audit, all 55 dated 2026-07-05), skills_by_level.md,
  salary_benchmarks.md, reports/2026-07-06.md. Confirmed `python3 analysis_gen.py 2026-07-06` runs clean
  (EXIT 0, N=769, new=0); re-verified RUN=1900-01-01 first-run path (EXIT 0, scratch report removed).
  **Made NO code change** (deliberate skip; "if warranted" not met): (a) the robustness features the
  2026-07-05 audit escalated as regressed in committed HEAD `d9123a2` are ALL already restored —
  `_split_skills`+`ast` (0 residual list-repr tokens), `natural language processing→NLP` (NLP=98),
  `golang→Go` (Go=10, Golang=0), §4 tie-break `(-x[3], x[0])` — and the contradictory
  `data warehousing→Data Warehouse` fold was reverted (git `1e1598f` added it, `f2f4173` reverted it);
  (b) swept all tokens at N=769 through the full `canon()` pipeline — **0 residual case splits, 0 residual
  list-repr tokens** — and the only cross-form clusters clearing the strict n≥3-both-forms bar are all
  STANDING KEEP-SPLITS (`GCP Vertex AI`/`Vertex AI`, `data analysis`/`data analytics`, `Speech
  Recognition`/`Speech-to-Text`, `Multimodal AI`/`multimodal models`, `REST API`/`REST APIs`, `C++`/`C#`
  false-positive; `Data Warehouse`(4)/`Data Warehousing`(now 0) no longer clears the bar) → correct
  action = no new fold. Country mix clean `{Germany 427, Switzerland 188, Austria 154}`; all 769
  locations resolve to a DACH country. Salary logic clean: **123 rows disclose pay (12 CHF)**, AT ×14 /
  CHF→EUR pinned 1.05 / hourly ×40×52 all render. jobs.csv, schema, and dedup formula untouched. Backlog:
  #9 recovery INTACT (extraction side still OPEN); #7 remains top operational risk; #1/#3/#5/#8/#10 DONE.
- **2026-07-05** (self-improvement meta-run on Opus): audited analysis_gen.py, LEARNINGS.md, jobs.csv
  (**714 rows, 0 ragged, 0 empty job_id, 0 duplicate job_id, 0 extra-column rows** — 22 cols every row;
  +11 vs the 703 at the 2026-07-04 audit, all 11 dated 2026-07-04), skills_by_level.md,
  salary_benchmarks.md, reports/2026-07-05.md. Confirmed `python3 analysis_gen.py 2026-07-05` runs clean
  (EXIT 0, N=714, new=0); re-verified RUN=1900-01-01 first-run path (scratch report removed). **Made NO
  code change** (deliberate skip): the only strict n≥3-both-forms cross-form alias candidate was
  `Data Warehouse`/`Data Warehousing`, an EXPLICIT standing 2026-07-04 keep-split → correct action = no
  new fold. **Found + escalated two problems in the committed HEAD `d9123a2` (a parallel meta-instance's
  commit):** (1) it reverted `analysis_gen.py` to an older base that DROPPED the 2026-07-01
  `_split_skills`/`ast` list-repr parser — **54 list-repr rows (7.6%) now mangled in every skills table**
  — plus the `natural language processing→NLP` (07-03) and `golang→Go` (07-04) folds and the §4
  deterministic tie-break; (2) it added `data warehousing→Data Warehouse`, contradicting the 2026-07-04
  keep-split (latent, below table cutoffs). Did NOT do in-race code surgery (harness flagged the external
  edit as intentional; additive-only / one-change / skip-if-unsure) — documented as **top repair priority
  for next run** (restore `_split_skills`+folds+tie-break, revert the data-warehousing fold). jobs.csv,
  schema, and dedup formula untouched.
- **2026-07-04** (self-improvement meta-run on Opus): audited analysis_gen.py, LEARNINGS.md,
  jobs.csv (**703 rows, 0 ragged, 0 empty job_id, 0 duplicate job_id, 0 extra-column rows** — all 22
  columns present on every row), skills_by_level.md, salary_benchmarks.md, reports/2026-07-04.md.
  Confirmed `python3 analysis_gen.py 2026-07-04` runs clean (EXIT 0, N=703, new=0) BEFORE and AFTER the
  change; re-verified on RUN=1900-01-01 (prev=0 first-run path) and RUN=2026-07-02 (new=32) — all three
  deliverables generate on every path (scratch 1900-01-01 report removed). **One additive, verified
  change to `analysis_gen.py`; jobs.csv and its schema untouched:** added `_SKILL_ALIASES` synonym fold
  `golang → Go` (the one clear cross-form split meeting the n≥3-both-forms bar: `Golang`(3) → canonical
  `Go`(7) → **Go 10**; same class as `k8s→Kubernetes`). Full-token verified: the alias maps only the
  exact token `golang` and never touches `Go` or substrings. Swept N=703: **0 residual case splits, 0
  residual list-repr tokens** after `canon()`. Considered but did NOT fold `GCP Vertex AI`(4)/`Vertex
  AI`(6) — deferred to the standing curated sub-service decision despite the SageMaker vendor-prefix
  inconsistency (flagged for reconsideration); also left split data analysis/analytics, Speech
  Recognition/Speech-to-Text, Data Warehouse/Warehousing, Multimodal AI/multimodal models (borderline
  word-form/scope), C++/C#, REST API/REST APIs (all per prior decisions / skip-if-unsure). Did NOT
  change: dedup formula; `_CASE_MAP`; CHF→EUR `to_eur()`; AT ×14 / hourly ×40×52; trend logic; defensive
  CSV read; `country()`/`_CITY_COUNTRY` (country mix clean `{Germany 393, Switzerland 177, Austria 133}`,
  all no-comma/slashed/parenthetical locations resolve). Backlog: #1 DONE (extended); #7 remains top
  operational risk; #9 OPEN but stable (108 legacy list-repr cells recovered by `_split_skills`; 0/24 new
  2026-07-03 rows used list-repr).
- **2026-07-03** (self-improvement meta-run on Opus): audited analysis_gen.py, LEARNINGS.md,
  jobs.csv (**679 rows, 0 ragged, 0 empty job_id, 0 duplicate job_id, 0 extra-column rows** — all 22
  columns present on every row), skills_by_level.md, salary_benchmarks.md, reports/2026-07-03.md.
  Confirmed `python3 analysis_gen.py 2026-07-03` runs clean (EXIT 0, N=679, new=0) BEFORE and AFTER
  the change; re-verified on RUN=1900-01-01 (prev=0 first-run path), RUN=2026-07-02 (new=32) and
  RUN=2026-07-01 (new=55) — all three deliverables generate on every path (scratch 1900-01-01 report
  removed). **One additive, verified change to `analysis_gen.py`; jobs.csv and its schema untouched:**
  added `_SKILL_ALIASES` acronym fold `natural language processing → NLP` (the only cross-form split
  meeting the n≥3-both-forms bar: `Natural Language Processing`(12) → dominant acronym `NLP`(77) →
  **NLP 89**; same class as `large language models→LLMs`). Full-token verified: `medical NLP`,
  `NLP Transformers`, `NLP publications`, `NLP project experience` all survive distinct. Swept N=679:
  **0 residual case splits, 0 residual list-repr tokens** after `canon()`. Did NOT change: dedup
  formula; `_CASE_MAP`; CHF→EUR `to_eur()`; AT ×14 / hourly ×40×52; trend logic; defensive CSV read;
  `country()`/`_CITY_COUNTRY` (country mix clean `{Germany 379, Switzerland 169, Austria 131}`, all
  no-comma/slashed/parenthetical locations resolve — no new entries). No other aliases warranted
  (MLOps/ML Ops, AI Automation/AI-Automation, Multimodal AI second forms all n=1; C++/C# distinct;
  REST API/REST APIs deliberately split). Backlog: #1 DONE (extended); #7 remains top operational
  risk; #9 OPEN but stable (108 legacy list-repr cells, all recovered by `_split_skills`).
- **2026-07-02** (self-improvement meta-run on Opus): audited analysis_gen.py, LEARNINGS.md,
  jobs.csv (**679 rows, 0 ragged, 0 empty job_id, 0 duplicate job_id, 0 extra-column rows**),
  skills_by_level.md, salary_benchmarks.md, reports/2026-07-02.md. Confirmed
  `python3 analysis_gen.py 2026-07-02` runs clean (EXIT 0, N=679, new=32) BEFORE and AFTER the
  changes; re-verified on RUN=1900-01-01 (prev=0 first-run path) and RUN=2026-07-01 (new=55) — all
  three deliverables generate on every path. **Two additive, verified changes to `analysis_gen.py`;
  jobs.csv and its schema untouched:** (1) two new `_SKILL_ALIASES` folds —
  `recommendation systems→recommender systems` (5+9→14) and `vision-language models→vision language
  models` (1+3→4), both cross-form/hyphen splits the case-fold can't bridge, mirroring the existing
  time-series / infrastructure-as-code folds; distinct compounds (`real-time recommender systems`,
  `Vision Transformers`) verified to survive. (2) deterministic §4 tie-break (backlog #10) —
  `dist.sort` key changed from `-gap` to `(-gap, skill)` so equal-gap skills no longer swap order
  between runs. All three deliverables byte-identical before/after (folds sit below top-N cutoffs;
  no §4 tie reordered this run) — zero output regression. Swept N=679: **0 residual case splits, 0
  residual list-repr tokens** after `canon()`. Did NOT change: dedup formula; `_CASE_MAP`; CHF→EUR
  `to_eur()`; AT ×14 / hourly ×40×52; trend logic; defensive CSV read; `country()`/`_CITY_COUNTRY`
  (all 32 new locations are clean `"City, Country"`, no new entries needed). Backlog: #10 DONE; #9
  still OPEN but improving (0/32 new rows used list-repr, vs 54/116 on 06-30; 108 legacy cells remain,
  all recovered by `_split_skills`); #7 remains top operational risk (all 3 primary boards still
  proxy-blocked — 32 kept jobs from WebSearch + ATS/career pages: greenhouse.io, ashbyhq.com,
  smartrecruiters, bmwgroup.jobs, etc.).
- **2026-06-30** (self-improvement meta-run on Opus): audited analysis_gen.py, LEARNINGS.md,
  jobs.csv (**592 rows, 0 ragged, 0 empty job_id, 0 duplicate job_id**), salary_benchmarks.md,
  skills_by_level.md, reports/2026-06-29.md. Confirmed `python3 analysis_gen.py 2026-06-30` runs clean
  (EXIT 0, N=592, new=116) BEFORE and AFTER the change; re-verified in a scratch copy on RUN=1900-01-01
  (prev=0 first-run path) and RUN=2026-06-29 — all three deliverables generate on every path.
  **One additive, verified change to `analysis_gen.py`; jobs.csv and its schema untouched:**
  (1) **list-repr skill parsing (`_split_skills`, NEW backlog #9).** 54 of the 116 new rows stored
  `required_skills`/`nice_to_have_skills` as a stringified Python list (`"['Python', 'PyTorch', …]"`,
  no `;`); the naive `;`-split counted each blob as ONE bogus token, making every skill in ~47% of the
  run invisible to the analysis. Added `_split_skills(field)`: detects `[...]`-with-no-`;` cells and
  expands them via `ast.literal_eval`; all other cells fall through to the exact prior `;`-split, so
  well-formed rows are byte-for-byte unchanged. Wired into `sk()`, `nth()`, and `_build_case_map()`.
  Verified: 0 residual list-repr tokens after the fix; recovered counts e.g. `Python` 536,
  `Machine Learning` 206, `PyTorch` 164. Import of `ast` added at top.
  Did NOT change: jobs.csv schema/columns; the dedup formula; `_SKILL_ALIASES` (no new alias warranted
  — residual near-dups are `C++`/`C#`, n=1 hyphen pairs, left split per skip-if-unsure); the generic
  `_CASE_MAP`; CHF→EUR `to_eur()` (handles the 2 new CHF rows — CERN + Novartis Basel — correctly at
  the pinned 1.05 rate); the AT ×14 monthly / hourly ×40×52 conventions; trend logic; the defensive
  CSV read; `country()` (clean mix `{Germany 331, Switzerland 145, Austria 116}` — the 3 pre-existing
  slashed rows still resolve via `_CITY_COUNTRY`; today's `Germany (Remote)` rows strip cleanly).
  Backlog status: NEW **#9** (extraction must emit `";".join(skills)`, not `str(list)`) logged as HIGH
  PRIORITY — same class as #1b but more urgent (silently zeroes rows). #7 (discovery resilience under
  egress block) remains the top operational risk — all 116 jobs came from WebSearch + unblocked
  ATS/career hosts (new working hosts logged in the Source reliability / 2026-06-30 notes); SAP Careers
  and Helsing/Aleph Alpha/Siemens were heavy contributors this run.
- **2026-06-29** (self-improvement meta-run on Opus): audited analysis_gen.py, LEARNINGS.md,
  jobs.csv (**476 rows**, parses clean), salary_benchmarks.md, skills_by_level.md. Confirmed
  `python3 analysis_gen.py 2026-06-29` runs clean (EXIT 0, N=476, new=52) BEFORE and AFTER the
  changes; re-verified in a scratch copy on RUN=1900-01-01 (prev=0 first-run path) and RUN=2026-06-28
  (new=17) — all three deliverables generate on every path. **Two additive, verified changes to
  `analysis_gen.py`; jobs.csv and its schema untouched:**
  (1) **CHF→EUR salary conversion (backlog #3, now DONE).** Added pinned `CHF_TO_EUR = 1.05` and a
  `to_eur()` helper. The disclosed-salaries table keeps original currency/values and gains a new
  "~Annualised (EUR-eq)" column; the by-role median pool now includes CHF rows converted to EUR
  (previously EUR-only, so all 9 CH salary rows were excluded). Verified outputs, e.g. PEAX 160k CHF →
  168k EUR, Anthropic 480k CHF → 504k EUR, CERN 42k CHF → 44k EUR. Other currencies return None and
  stay out of the EUR pool. The stale "Switzerland still discloses no salaries" note was corrected.
  (2) **Time-series alias consolidation.** Changed the two `time(-) series analysis` aliases to fold
  to `Time Series Forecasting` instead of a separate `Time Series Analysis` canonical, so all five
  raw spellings now collapse to one token (verified via `canon()`). Full-token fold, not substring.
  Did NOT change: jobs.csv schema/columns; the dedup formula; the generic `_CASE_MAP` (already folds
  `Power BI` and `Machine Learning` casing correctly at N=476 — no new alias needed); the AT ×14
  monthly convention; the hourly ×40×52 convention; trend logic; the defensive CSV read; `country()`.
  Backlog status: #3 (CHF/EUR FX) now DONE; #7 (discovery resilience under egress block) remains the
  top operational risk (primary boards still proxy-blocked; 52 jobs this run came from WebSearch +
  unblocked ATS/career hosts — new working hosts logged in the Source reliability / 2026-06-29 notes).
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
