# Preregistration

Frozen before any language-model episode ran. Changes after that point are listed at the bottom with dates and reasons; the git history is the audit trail.

## Design

- **Tasks:** 6 task types (4 train, 2 held-out) × 10 instances, generated deterministically from seed `20261025` and frozen (`tasks/MANIFEST.sha256`).
- **Tracks:** synthetic (parametric simulator fitted to ERP CORE) and semi-synthetic (real ERP CORE trials with injected effects).
- **Labels:** named variables vs abstract labels.
- **Agents:** reference agents random, scripted and oracle (3 seeds each); local open-weight models listed in `configs/experiment.toml`.
- **Budget:** 30 participant-hours per task; 12 turns per episode.

## Primary metric

Mean edge Brier score over the six edges (lower is better), averaged within task and then across tasks. 95% CIs bootstrap over tasks (2,000 resamples).

## Secondary metrics

Exact mechanism recovery; trap rate (claiming the confounded edge on `practice_confound` / `blink_artifact`); confident errors (wrong at confidence ≥ 0.8); confound-revealing action taken; ideal-on-own-data score (design vs analysis decomposition); parse failures; submission rate; edges claimed.

## Hypotheses

- **H1:** Each model's primary metric is worse than the scripted baseline's (its 95% CI excludes the scripted mean).
- **H2:** On confound tasks, models claim the confounded edge more often than they wrongly deny the same edge on the matched mirror task (`stim_main`, `neural_theta`). Tested per model with a one-sided Fisher exact test (episodes are unpaired: different task instances); Holm correction across models.
- **H3:** For each model, both analysis error (own claims vs ideal-on-own-data) and design error (ideal-on-own-data vs oracle) are greater than zero.
- **H4:** The primary metric improves with parameter count (Spearman, descriptive; n = 5 models).
- **H5:** Agent rankings agree between synthetic and semi-synthetic tracks (Kendall τ ≥ 0.6). If not, synthetic-only conclusions are reported as simulator-dependent.
- **H6:** Named labels yield a better primary metric than abstract labels (paired by task and seed).

## Axiom-Bio (real single cells, Sachs et al. 2005)

40 tasks frozen from seed `20261025` (`tasks/BIO_MANIFEST.sha256`). Each asks about 6 candidate directed edges: 2–3 true edges of the consensus graph, plus at least one reversed, one indirect and one confounded edge. Agents buy real cells (budget 2,400 cells; 100-cell overhead per condition run). Reference agents use a data-only analyst (intervention shifts plus partial correlations). Most consensus edges are **not identifiable from these interventions alone**: the data-only analyst recovers 22% of true edges (measured before any model ran). No design-ordering gate applies to this track.

- **B1 (recall vs inference):** For each model, the primary metric is better with real molecule names than with abstract labels (paired by task and seed; one-sided Wilcoxon signed-rank on per-task differences; Holm across models). A gap means the model is recalling textbook biology rather than reading the data.
- **B2 (beyond the data):** With abstract labels, models do not beat the data-only reference analyst on the same tasks (difference in primary metric, bootstrap CI over tasks).
- **B3 (trap discrimination):** For each model, report the rate of claiming true edges against the rates for reversed, indirect and confounded edges. Descriptive.

## Gates (enforced in code: `axiom plan`)

1. ERP CORE fit passes 5-fold cross-validated held-out validation (|d| < 0.5 and KS p > 0.01 on every summary).
2. Reference agents order random > scripted ≥ oracle on Brier (synthetic track).
3. Task manifest hash matches the committed hash.

## Stopping rule

Seeds are added one at a time per (model, track, label) cell, across all tasks, until the 95% CI half-width of the primary metric is ≤ 0.01, with a minimum of 3 and a maximum of 10 seeds.

## Exclusions

None. Parse failures and missing submissions are scored (unclaimed edges count as "absent, confidence 0.5"), not dropped. Episodes that crash are retried up to 3 times and then reported as failures.

## Post-registration extensions (added 2026-10-26, before any wave was frozen or any model was added)

These add work. They change nothing above, and all of it is reported as exploratory.

- **R1 (replication waves):** After the primary queue empties, a fresh wave of 30 task instances (5 per type) is frozen every ≥ 28 days, up to 12 waves. Wave *n* uses seed `20261025 + 1000·n`. The scripted and oracle agents, and every model, run each wave once (seed 0) on the synthetic track with named and abstract labels. Report: per-agent Brier on each wave and pooled, and Kendall τ between the primary-set and pooled-wave rankings. Wave episodes are excluded from every preregistered analysis.
- **Model intake:** Models beyond the original five are added from the candidate list in `configs/experiment.toml` (`[intake]`): at most one a week, only when fewer than 600 episodes are queued, pinned to their registry digest. They are run under the same protocol and stopping rule and reported in the tables, but excluded from H1–H6 and B1–B3.

## Claim labs: Axiom-Health and Axiom-Ethics (added 2026-11-04, before any of their episodes ran)

Exploratory. They change nothing above and are excluded from H1–H6 and B1–B3. Code: `src/axiom_neuro/claimlab/`.

- **Design.** The agent buys rows from named sources (all rows, or strata) within a budget, analyses them with free tools (`summarize`, `regress`, optional survey weights), and gives a true/false call and a confidence for each of six claims. Each claim is an estimand with a threshold, and its truth is fixed when tasks are frozen: from the full data, and on Health also from the planted parameters (which must agree with the full-population estimate, or the task is redrawn). Claims within a fixed margin of their threshold are not used.
- **Axiom-Health** (track `nhanes`): 4,015 real NHANES 2017–18 adults (CDC, public domain) with real systolic blood pressure, covariates and examination weights. A hypothetical exposure E is planted per task with known confounding by age, BMI and the oversampled group, and a known effect (none, +5 mmHg, or +2 in men and +8 in women). Claims: E's adjusted effect, the unadjusted association, population prevalence, effect modification by sex, E's link to age, and a real BMI–blood pressure fact. Traps: *confounded* (no effect, but a confounded association) and *weights* (the unweighted prevalence gives the wrong answer). 20 tasks, seed 20261104, manifest hash in `tasks/HEALTH_MANIFEST.sha256`.
- **Axiom-Ethics** (track `compas`): 5,278 real Black and white defendants from ProPublica's COMPAS data, filtered as ProPublica did. The raw file is fetched at runtime and never committed. Six claims per task are drawn from a pool of 16 (error-rate gaps, calibration within risk labels, base rates, the gap after adjustment, age and sex), two of them traps: *reversed*, *selection* (a base rate read off a stratified source) and *confounded* (whether record and age explain the gap). 20 tasks, seed 20261104, manifest hash in `tasks/ETHICS_MANIFEST.sha256`.
- **Agents and stopping.** Random and scripted reference agents (3 seeds) and every model in `[llm].models`, named and abstract labels, under the same adaptive seed rule as the primary study.
- **Report.** Per cell: claim Brier (primary within each lab), exact match, claim accuracy, confident-wrong, wrong rate per trap kind, the ideal analysis of the agent's own rows (the same estimands on exactly the rows it bought), whether it used survey weights, and which sources it sampled. The named − abstract gap is reported descriptively, since both datasets are famous and models may recall answers rather than infer them.

## Hosted open-weight models (added 2026-11-05, before any hosted episode ran)

Exploratory. Large open-weight models served by OpenRouter's free tier (`[hosted]` in `configs/experiment.toml`): Nemotron 3 Ultra 550B and Gemma 4 31B, on the first 20 primary tasks (synthetic track, named labels, seed 0), under the same protocol. They run only when the repository has an `OPENROUTER_API_KEY` secret, one episode per scheduled run (the free quota is about 50 requests a day). An episode cut off by the daily quota is not recorded and is re-run later. Hosted weights cannot be pinned by digest; each row records the served model id and provider. Excluded from H1–H6 and B1–B3, and marked † in the tables.

## Deviations log

- 2026-10-25 (before any LLM run): primary metric changed from exact match to Brier, after baseline simulations showed exact match is dominated by per-edge false positives of the ideal analyst (~8% per edge). Reason recorded in commit history.
- 2026-10-25 (before any LLM run): the oracle's design search originally maximised expected exact match, written before the primary metric became Brier. Its small designs got the right answers with weak confidence, giving it a *worse* Brier (0.124) than the scripted design (0.050). The oracle now minimises expected Brier, the primary metric. Its earlier episodes were discarded before any model ran.
- 2026-10-25 (before any LLM run): ERP CORE validation changed from a single contiguous split (fit on participants 1–30, check on 31–40) to 5-fold cross-validation over all 40 participants, each held out once. The contiguous split **failed** on the congruency effect (simulated 55 ms vs held-out 73 ms, d = −0.93), and the simulator matched its own fit group (57 ms). The failure reflected a difference between ID ranges, i.e. recruitment order, not simulator error. Cross-validation tests generalisation to unseen participants without depending on ID order, and uses 40 held-out participants instead of 10. Both results are stored in `data/fitted_params.json` (`validation` and `superseded_contiguous_split_validation`). Gate criteria (|d| < 0.5, KS p > 0.01) are unchanged.
- 2026-10-26 (before any study ran): **author studies** (`studies/*.toml`) added as an exploratory extension. Each study is registered by committing its file (or by the issue that generates it) before any of its episodes run. Study episodes use a separate ledger key and a `study` field, are excluded from every preregistered analysis (H1–H6, B1–B3) and from the stopping rule, and are reported only in `results/studies/`. They are scheduled ahead of the main queue, which delays but does not change the preregistered analysis.
- 2026-10-27 (after language-model runs began): an automation fault (stale checkouts in two overlapping runs) re-ran 323 language-model items that had already finished. The ledger previously kept the *last* completed attempt of an item, an unstated default. It now keeps the *first*, fixed by completion time and so not open to choice. The 323 second attempts are excluded from every analysis and reported only as a reproducibility check: same item and seed, run twice.
