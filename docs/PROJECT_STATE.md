# Project state

The handoff file: read this first. Last updated 2026-10-25.

## Where things stand

- **Built:** both labs (Axiom-Neuro, Axiom-Bio), reference agents, local-LLM agent, judge-free scoring, ledger, planner with gates and adaptive seeds, report, figures, episode animations, paper with generated tables, project page, and four GitHub workflows (ci, experiments, site, watchdog).
- **ERP CORE fit:** done and validated with 5-fold CV (all |d| ≤ 0.28). Parameters are in `data/fitted_params.json`.
- **Task sets:** frozen. Neuro has 60 tasks, bio has 40. Hashes are in `tasks/*.sha256`.
- **Reference agents:** run locally through the same pipeline the automation uses. Results are in `results/ledger.jsonl`.
- **Language-model runs:** happen automatically once the baseline-order gate passes. They run on GitHub Actions every 6 hours.

## Decisions on record

Full reasons for each are in `PREREGISTRATION.md`, deviations log.

1. The primary metric is Brier, not exact match. This was decided before any language-model run.
2. ERP CORE validation uses 5-fold CV. The first contiguous split failed on the congruency effect, and that failure is recorded.
3. The oracle minimises expected Brier. An earlier exact-match oracle and its episodes were discarded before any language-model run.
4. The bio track has no design-ordering gate: most of the consensus graph can't be identified from the data. Its hypotheses (B1–B3) target recall versus inference instead.

## Open items for the author

- **arXiv submission** needs your arXiv account, and your first submission in a category needs an endorsement. Each paper build produces `arxiv-source.tar.gz` on the project site and as a workflow artifact.
- **Actions terms:** if you'd rather not run sustained compute on GitHub-hosted runners, register your Mac as a self-hosted runner and set the repository variable `AXIOM_RUNNER=self-hosted`.
