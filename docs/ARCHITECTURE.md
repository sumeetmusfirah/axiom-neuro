# Architecture

```
configs/experiment.toml      what to run (models, tracks, seeds, gates)  <- the only file you edit to change the study
src/axiom_neuro/
  mechanisms.py              hypothesis family: 6 edges, 6 task types, planted traps, mirror tasks
  design.py                  experiment designs, validation, participant-hour cost
  simulator.py               synthetic + semi-synthetic (real ERP CORE trials) data generation
  params.py                  simulator parameters (defaults until fitted)
  erpcore/fit.py             download ERP CORE, extract trials/theta/blinks, fit, held-out validation
  analysis.py                cluster-robust OLS, ideal analyst, the agent's analysis tools
  env.py                     the lab: pilot data, budget, actions, episode log
  agents/baselines.py        random / scripted / simulation-optimal oracle
  agents/llm.py              local LLM via Ollama, schema-constrained JSON actions
  scoring.py                 judge-free scoring against ground truth
  tasks.py                   deterministic task set, freeze + hash
  ledger.py                  append-only results, idempotent by key
  planner.py                 gates, work queue, adaptive seeds, sharding
  runner.py                  run one shard under a wall-clock budget
  report.py / figures.py /   RESULTS.md, figures, episode animations, paper tables
  animate.py / paper.py
.github/workflows/
  ci.yml                     tests + smoke on every push
  experiments.yml            every 6h: plan -> setup | shards -> collect -> report -> commit
  site.yml                   after each run: figures, animations, paper PDF -> GitHub Pages
  watchdog.yml               daily: opens an issue if runs stall or a gate fails
```

## The loop

```
cron (6h) ──> plan ──┬─ setup needed? ──> fit ERP CORE ─> oracle designs ─> freeze tasks ─> commit
                     └─ work queued?  ──> N parallel shards (one model each, Ollama on the runner)
                                              │  each episode appended to a shard file as it finishes
                                              ▼
                                         collect ─> ledger.jsonl ─> RESULTS.md ─> commit (only if new rows)
                                              ▼
                                         site: figures + animations + paper PDF ─> Pages
```

## Why it keeps running and when it stops

- **Resumable by construction.** Work is the set difference between what the config asks for and what the ledger holds. A killed job loses only the episode in flight; the next run re-plans it.
- **Idempotent.** Every attempt has a unique id; collecting twice adds nothing. Crashes are logged and retried up to 3 times.
- **Gated.** `plan` refuses to queue model runs until the ERP CORE fit validates, the reference agents order correctly and the task manifest matches its hash.
- **Self-terminating.** The adaptive seed rule stops each cell when its primary-metric CI is tight enough. When nothing is left, runs become no-ops and make no commits.
- **Extensible.** Add a model to `configs/experiment.toml` and the next run queues it. Nothing else changes.
- **No empty commits.** Reports stamp the latest data time, not the clock, so a run with no new data leaves the tree byte-identical.

## Cost

$0. GitHub-hosted runners are free for public repositories, and models run locally on the runner with Ollama. Parallelism is capped at 4 jobs. GitHub's Actions terms tie usage to the repository's own software project. These runs are this project's benchmark, but sustained heavy compute is a judgement call. If in doubt, register your own machine as a self-hosted runner and set the repository variable `AXIOM_RUNNER=self-hosted`. The workflows use it unchanged.
