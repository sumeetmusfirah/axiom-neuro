# Axiom-Neuro results

Auto-generated from `results/ledger.jsonl` (data as of 2026-10-26T18:30:38.827644+00:00). Do not edit by hand.

**Progress:** 1656 episodes scored, 12 failed attempts logged, 1624 queued. Setup pending: none.

## Gates

| Gate | Passed | Detail |
| --- | --- | --- |
| fit_validated | yes | `{"params_source": "erpcore-ern"}` |
| tasks_frozen | yes | `{}` |
| baseline_order | yes | `{"metric": "brier (lower is better)", "means": {"random": 0.1202, "scripted": 0.0499, "oracle": 0.0408}}` |

## Results: Axiom-Neuro, synthetic track

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| oracle | named | 180 | 0.041 [0.036, 0.047] | 0.82 | 0.97 | 0.02 | 0.10 | 1.00 | 0.82 | 0.81 | 0.85 |
| scripted | named | 180 | 0.050 [0.043, 0.058] | 0.74 | 0.95 | 0.06 | 0.12 | 1.00 | 0.74 | 0.71 | 0.82 |
| random | named | 180 | 0.120 [0.107, 0.134] | 0.46 | 0.87 | 0.32 | 0.08 | 0.69 | 0.46 | 0.49 | 0.38 |

## Results: Axiom-Neuro, semi-synthetic track (real ERP CORE trials)

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| oracle | named | 180 | 0.044 [0.039, 0.049] | 0.77 | 0.96 | 0.03 | 0.18 | 1.00 | 0.77 | 0.75 | 0.80 |
| scripted | named | 180 | 0.049 [0.044, 0.053] | 0.76 | 0.96 | 0.03 | 0.15 | 1.00 | 0.76 | 0.77 | 0.73 |
| random | named | 180 | 0.098 [0.086, 0.111] | 0.57 | 0.91 | 0.14 | 0.08 | 0.69 | 0.57 | 0.54 | 0.62 |
| qwen3:4b | abstract | 10 | 0.186 [0.128, 0.239] | 0.10 | 0.77 | 0.80 | 0.00 | 0.80 | 0.80 | 0.10 | – |
| llama3.2:3b | abstract | 46 | 0.289 [0.268, 0.311] | 0.00 | 0.63 | 0.74 | 0.44 | 0.73 | 0.74 | 0.00 | 0.00 |
| gemma3:4b | abstract | 10 | 0.302 [0.224, 0.383] | 0.00 | 0.60 | 1.20 | 0.40 | 1.00 | 0.70 | 0.00 | – |

## Results: Axiom-Bio (real single cells, Sachs et al. 2005)

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen3:4b | abstract | 30 | 0.256 [0.250, 0.263] | 0.00 | 0.58 | 0.13 | 0.13 | – | 0.00 | 0.00 | – |
| qwen3:4b | named | 35 | 0.256 [0.248, 0.264] | 0.00 | 0.58 | 0.14 | 0.14 | – | 0.00 | 0.00 | – |
| llama3.2:3b | named | 40 | 0.266 [0.251, 0.283] | 0.03 | 0.60 | 0.42 | 0.38 | – | 0.00 | 0.03 | – |
| gemma3:4b | named | 40 | 0.272 [0.252, 0.293] | 0.00 | 0.57 | 0.35 | 0.35 | – | 0.00 | 0.00 | – |
| random | named | 120 | 0.274 [0.260, 0.288] | 0.00 | 0.57 | 1.50 | 0.38 | – | 0.00 | 0.00 | – |
| qwen3:14b | abstract | 14 | 0.276 [0.249, 0.306] | 0.00 | 0.56 | 0.50 | 0.64 | – | 0.00 | 0.00 | – |
| scripted | named | 120 | 0.276 [0.255, 0.300] | 0.00 | 0.62 | 1.68 | 0.26 | – | 0.00 | 0.00 | – |
| llama3.2:3b | abstract | 40 | 0.280 [0.258, 0.306] | 0.00 | 0.57 | 0.53 | 0.42 | – | 0.00 | 0.00 | – |
| gemma3:4b | abstract | 40 | 0.296 [0.275, 0.319] | 0.00 | 0.53 | 0.82 | 0.45 | – | 0.00 | 0.00 | – |
| mistral:7b | abstract | 31 | 0.308 [0.272, 0.350] | 0.00 | 0.53 | 0.74 | 0.29 | – | 0.00 | 0.00 | – |

## Preregistered hypotheses (see PREREGISTRATION.md)

- **H1** (pending): waiting for data
- **H2** (pending): waiting for data
- **H3** (pending): waiting for data
- **H4** (pending): waiting for data
- **H5** (pending): waiting for data
- **H6** (pending): waiting for data
- **B1** (evaluated): llama3.2:3b: Brier abstract - named = +0.014 over 40 tasks, Holm p = 0.326; qwen3:4b: Brier abstract - named = -0.000 over 25 tasks, Holm p = 0.433; gemma3:4b: Brier abstract - named = +0.024 over 40 tasks, Holm p = 0.16
- **B2** (evaluated): llama3.2:3b: Brier model - reference = +0.004 [-0.027, +0.034]; qwen3:4b: Brier model - reference = -0.025 [-0.053, +0.000]; gemma3:4b: Brier model - reference = +0.020 [-0.010, +0.048]; mistral:7b: Brier model - reference = +0.026 [-0.022, +0.077]; qwen3:14b: Brier model - reference = +0.010 [-0.019, +0.039]
- **B3** (evaluated): llama3.2:3b: claims true 0.23 / reversed 0.11 / indirect 0.16 / confounded 0.12; qwen3:4b: claims true 0.08 / reversed 0.07 / indirect 0.03 / confounded 0.07; gemma3:4b: claims true 0.31 / reversed 0.22 / indirect 0.20 / confounded 0.29

## Reproducibility of seeded episodes

323 items were run twice with the same seed (an automation fault re-ran finished work; the first completed attempt is the scored one). Local inference on CPU is not bit-deterministic, so the pairs measure run-to-run noise: 76% gave identical claims, mean |ΔBrier| = 0.020.

| Agent | Pairs | Identical claims | Mean abs. Brier difference | Max |
| --- | --- | --- | --- | --- |
| gemma3:4b | 90 | 53% | 0.038 | 0.248 |
| llama3.2:3b | 126 | 100% | 0.000 | 0.000 |
| mistral:7b | 31 | 16% | 0.082 | 0.299 |
| qwen3:14b | 14 | 100% | 0.000 | 0.000 |
| qwen3:4b | 62 | 82% | 0.010 | 0.109 |

## Replication waves (exploratory, R1)

No wave has run yet. The first wave is frozen once the primary queue is empty.
