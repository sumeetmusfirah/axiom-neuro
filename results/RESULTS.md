# Axiom-Neuro results

Auto-generated from `results/ledger.jsonl` (data as of 2026-11-05T03:59:55.264541+00:00). Do not edit by hand.

**Progress:** 4324 episodes scored, 86 failed attempts logged, 3216 queued. Setup pending: none.

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
| qwen3:14b | named | 58 | 0.128 [0.118, 0.139] | 0.79 | 0.96 | 0.14 | 0.20 | 1.00 | 0.79 | 0.80 | 0.78 |
| qwen3:4b | named | 120 | 0.165 [0.147, 0.181] | 0.28 | 0.80 | 0.42 | 0.25 | 0.79 | 0.79 | 0.26 | 0.30 |
| qwen3:4b | abstract | 120 | 0.190 [0.171, 0.210] | 0.12 | 0.76 | 0.89 | 0.15 | 0.78 | 0.82 | 0.07 | 0.20 |
| gemma3:4b | abstract | 120 | 0.231 [0.213, 0.249] | 0.11 | 0.72 | 0.71 | 0.38 | 0.90 | 0.88 | 0.03 | 0.28 |
| gemma3:4b | named | 120 | 0.245 [0.230, 0.261] | 0.11 | 0.71 | 0.57 | 0.28 | 0.94 | 0.88 | 0.09 | 0.15 |
| mistral:7b | named | 60 | 0.261 [0.228, 0.295] | 0.13 | 0.74 | 0.53 | 0.10 | 0.80 | 0.85 | 0.12 | 0.15 |
| mistral:7b | abstract | 60 | 0.277 [0.250, 0.305] | 0.02 | 0.69 | 0.88 | 0.20 | 0.90 | 0.83 | 0.00 | 0.05 |
| llama3.2:3b | abstract | 180 | 0.284 [0.270, 0.297] | 0.03 | 0.62 | 0.64 | 0.20 | 0.77 | 0.61 | 0.05 | 0.00 |
| llama3.2:3b | named | 188 | 0.298 [0.284, 0.313] | 0.03 | 0.60 | 0.82 | 0.32 | 0.70 | 0.65 | 0.04 | 0.02 |

## Results: Axiom-Neuro, semi-synthetic track (real ERP CORE trials)

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| oracle | named | 180 | 0.044 [0.039, 0.049] | 0.77 | 0.96 | 0.03 | 0.18 | 1.00 | 0.77 | 0.75 | 0.80 |
| scripted | named | 180 | 0.049 [0.044, 0.053] | 0.76 | 0.96 | 0.03 | 0.15 | 1.00 | 0.76 | 0.77 | 0.73 |
| random | named | 180 | 0.098 [0.086, 0.111] | 0.57 | 0.91 | 0.14 | 0.08 | 0.69 | 0.57 | 0.54 | 0.62 |
| qwen3:4b | named | 120 | 0.161 [0.141, 0.183] | 0.28 | 0.78 | 0.47 | 0.17 | 0.70 | 0.80 | 0.24 | 0.35 |
| qwen3:4b | abstract | 120 | 0.179 [0.157, 0.199] | 0.16 | 0.78 | 0.82 | 0.05 | 0.81 | 0.83 | 0.16 | 0.15 |
| gemma3:4b | named | 120 | 0.227 [0.212, 0.242] | 0.12 | 0.73 | 0.42 | 0.17 | 0.93 | 0.85 | 0.11 | 0.15 |
| gemma3:4b | abstract | 120 | 0.258 [0.240, 0.275] | 0.08 | 0.67 | 0.81 | 0.50 | 0.97 | 0.89 | 0.04 | 0.17 |
| mistral:7b | named | 45 | 0.267 [0.231, 0.308] | 0.11 | 0.72 | 0.51 | 0.00 | 0.72 | 0.80 | 0.11 | 0.10 |
| llama3.2:3b | abstract | 180 | 0.284 [0.270, 0.301] | 0.02 | 0.63 | 0.65 | 0.25 | 0.83 | 0.66 | 0.02 | 0.02 |
| llama3.2:3b | named | 180 | 0.301 [0.286, 0.317] | 0.03 | 0.59 | 0.87 | 0.40 | 0.78 | 0.72 | 0.05 | 0.00 |

## Results: Axiom-Bio (real single cells, Sachs et al. 2005)

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen3:4b | abstract | 40 | 0.255 [0.251, 0.261] | 0.00 | 0.58 | 0.15 | 0.10 | – | 0.00 | 0.00 | – |
| qwen3:4b | named | 43 | 0.259 [0.248, 0.273] | 0.00 | 0.57 | 0.21 | 0.19 | – | 0.00 | 0.00 | – |
| random | named | 120 | 0.274 [0.260, 0.288] | 0.00 | 0.57 | 1.50 | 0.38 | – | 0.00 | 0.00 | – |
| scripted | named | 120 | 0.276 [0.255, 0.300] | 0.00 | 0.62 | 1.68 | 0.26 | – | 0.00 | 0.00 | – |
| gemma3:4b | named | 80 | 0.277 [0.261, 0.295] | 0.00 | 0.58 | 0.53 | 0.35 | – | 0.00 | 0.00 | – |
| llama3.2:3b | named | 120 | 0.278 [0.265, 0.292] | 0.01 | 0.57 | 0.47 | 0.41 | – | 0.00 | 0.01 | – |
| qwen3:14b | abstract | 28 | 0.279 [0.260, 0.300] | 0.00 | 0.55 | 0.57 | 0.64 | – | 0.00 | 0.00 | – |
| gemma3:4b | abstract | 75 | 0.281 [0.266, 0.298] | 0.00 | 0.58 | 0.61 | 0.41 | – | 0.00 | 0.00 | – |
| llama3.2:3b | abstract | 120 | 0.283 [0.267, 0.302] | 0.01 | 0.57 | 0.58 | 0.42 | – | 0.00 | 0.01 | – |
| mistral:7b | named | 22 | 0.298 [0.258, 0.348] | 0.00 | 0.58 | 0.73 | 0.41 | – | 0.00 | 0.00 | – |
| mistral:7b | abstract | 40 | 0.308 [0.277, 0.345] | 0.00 | 0.55 | 0.78 | 0.33 | – | 0.00 | 0.00 | – |

## Results: Axiom-Health (exploratory; real NHANES 2017-18 adults, planted exposure)

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| scripted | named | 60 | 0.018 [0.011, 0.027] | 0.88 | 0.98 | 0.02 | 0.02 | – | 0.88 | 0.88 | – |
| random | named | 60 | 0.061 [0.041, 0.083] | 0.55 | 0.91 | 0.18 | 0.25 | – | 0.55 | 0.55 | – |

## Results: Axiom-Ethics (exploratory; real COMPAS risk scores, ProPublica)

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| scripted | named | 60 | 0.014 [0.009, 0.019] | 0.93 | 0.99 | 0.00 | 0.00 | – | 0.93 | 0.93 | – |
| random | named | 60 | 0.130 [0.102, 0.160] | 0.40 | 0.84 | 0.60 | 0.32 | – | 0.40 | 0.40 | – |

† Added after preregistration by model intake or as a hosted model (see `configs/experiment.toml`, `[intake]` and `[hosted]`). Reported, but excluded from the preregistered tests.

## Preregistered hypotheses (see PREREGISTRATION.md)

- **H1** (evaluated): 5/5 models' Brier CI lies wholly above (worse than) the scripted baseline (0.050).
- **H2** (evaluated): llama3.2:3b: trap 0.32 vs mirror denial 0.58, Holm p = 1; qwen3:4b: trap 0.25 vs mirror denial 0.30, Holm p = 1; gemma3:4b: trap 0.28 vs mirror denial 0.38, Holm p = 1; mistral:7b: trap 0.10 vs mirror denial 0.50, Holm p = 1; qwen3:14b: trap 0.20 vs mirror denial 0.11, Holm p = 1
- **H3** (evaluated): llama3.2:3b: own claims 0.03 vs ideal analysis of its data 0.65; qwen3:4b: own claims 0.28 vs ideal analysis of its data 0.79; gemma3:4b: own claims 0.11 vs ideal analysis of its data 0.88; mistral:7b: own claims 0.13 vs ideal analysis of its data 0.85; qwen3:14b: own claims 0.79 vs ideal analysis of its data 0.79
- **H4** (evaluated): Spearman rho(size, Brier) = -0.60 (negative = bigger is better; n = 5, p = 0.285)
- **H5** (evaluated): Kendall tau synthetic vs semi-synthetic agent ranking = 1.00 (n = 7)
- **H6** (evaluated): llama3.2:3b: Brier abstract - named = -0.014 (positive = names help); qwen3:4b: Brier abstract - named = +0.026 (positive = names help); gemma3:4b: Brier abstract - named = -0.014 (positive = names help); mistral:7b: Brier abstract - named = +0.016 (positive = names help)
- **B1** (evaluated): llama3.2:3b: Brier abstract - named = +0.005 over 40 tasks, Holm p = 1; qwen3:4b: Brier abstract - named = -0.004 over 40 tasks, Holm p = 1; gemma3:4b: Brier abstract - named = +0.004 over 40 tasks, Holm p = 1; mistral:7b: Brier abstract - named = +0.019 over 22 tasks, Holm p = 1
- **B2** (evaluated): llama3.2:3b: Brier model - reference = +0.006 [-0.023, +0.035]; qwen3:4b: Brier model - reference = -0.021 [-0.045, +0.002]; gemma3:4b: Brier model - reference = +0.005 [-0.022, +0.030]; mistral:7b: Brier model - reference = +0.032 [-0.007, +0.073]; qwen3:14b: Brier model - reference = -0.001 [-0.034, +0.030]
- **B3** (evaluated): llama3.2:3b: claims true 0.17 / reversed 0.12 / indirect 0.18 / confounded 0.13; qwen3:4b: claims true 0.10 / reversed 0.12 / indirect 0.04 / confounded 0.06; gemma3:4b: claims true 0.30 / reversed 0.23 / indirect 0.17 / confounded 0.25; mistral:7b: claims true 0.24 / reversed 0.27 / indirect 0.17 / confounded 0.11

## Reproducibility of seeded episodes

1021 items were run twice with the same seed (an automation fault re-ran finished work; the first completed attempt is the scored one). Local inference on CPU is not bit-deterministic, so the pairs measure run-to-run noise: 74% gave identical claims, mean |ΔBrier| = 0.024.

| Agent | Pairs | Identical claims | Mean abs. Brier difference | Max |
| --- | --- | --- | --- | --- |
| gemma3:4b | 270 | 53% | 0.041 | 0.369 |
| llama3.2:3b | 378 | 100% | 0.000 | 0.000 |
| mistral:7b | 90 | 43% | 0.060 | 0.407 |
| qwen3:14b | 42 | 43% | 0.036 | 0.192 |
| qwen3:4b | 241 | 74% | 0.028 | 0.297 |

## Replication waves (exploratory, R1)

No wave has run yet. The first wave is frozen once the primary queue is empty.
