# DACH Data/ML/AI Job Intelligence

Autonomous daily agent that scans Switzerland / Germany / Austria for
Data Science · ML Engineer · AI Engineer · Data Engineer · AI Researcher roles,
maintains a deduplicated database, and regenerates skills/salary analysis.

Full agent spec: [`CLAUDE.md`](CLAUDE.md).

## Files
| File | What it is |
|---|---|
| `jobs.csv` | Master deduplicated job database (one row per `job_id`) |
| `analysis_gen.py` | Regenerates the three reports below from `jobs.csv` |
| `skills_by_level.md` | **Primary** — most-requested skills per role × seniority, with trends |
| `salary_benchmarks.md` | Salary medians/ranges per role × seniority × country |
| `reports/YYYY-MM-DD.md` | Daily delta report (new jobs, breakdowns, sources) |

## Run a cycle manually
```
python3 analysis_gen.py 2026-06-27   # regenerate analysis for a given run date
```

## Schedule
Runs daily as a Claude Code cloud agent (07:00 Europe/Vienna). The cloud run
discovers new postings, dedupes into `jobs.csv`, regenerates the reports, and
commits the results back to this repo.

## Working sources
Arbeitnow API · datacareer.ch · karriere.at. LinkedIn/Indeed/StepStone/Glassdoor
are intentionally **not** scraped (auth/aggregator).
