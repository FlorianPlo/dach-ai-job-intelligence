# DACH Data/ML/AI Job Intelligence

Tracks Data Science · ML · AI Engineering · Data Engineering · AI Research roles in
Switzerland / Germany / Austria, keeps a deduplicated database, and generates
skills-by-level and salary analysis. Run on demand or monthly.

Agent spec: [`CLAUDE.md`](CLAUDE.md) · extraction spec: [`.claude/agents/job-extractor.md`](.claude/agents/job-extractor.md)

## How it works
1. `python3 jobs.py fetch` — Python pulls public job feeds (company ATS feeds, Bundesagentur
   für Arbeit, Arbeitnow, karriere.at), keeps only new relevant DACH postings, writes small
   batches to `inbox/<date>/`. No tokens spent.
2. Claude runs ~15–25 rotating web searches for what feeds miss (Indeed/LinkedIn snippets →
   company → original posting) and queues finds with `jobs.py add-url` / `add-company`.
3. Haiku subagents extract structured fields per batch.
4. `python3 jobs.py ingest` then `python3 jobs.py analyze`.

## Company index
`companies.csv` grows every run. To load a big list:
```
python3 jobs.py import-companies my_companies.csv   # columns like name, website, country
python3 jobs.py detect                              # finds each company's job feed (~1 min / 70)
python3 jobs.py status
```

## Outputs
`jobs.csv` (column `is_active`: yes / no / ?) · [`open_jobs.md`](open_jobs.md) (all open postings) ·
`skills_by_level.md` · `salary_benchmarks.md` · `reports/YYYY-MM-DD.md`

Re-check whether older postings are still online: `python3 jobs.py check-active` (default: not seen for 30+ days).
