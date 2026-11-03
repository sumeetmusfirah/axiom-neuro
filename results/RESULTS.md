# Axiom-Neuro results

Auto-generated from `results/ledger.jsonl` (data as of 2026-11-03T21:02:18.365273+00:00). Do not edit by hand.

**Progress:** 3003 episodes scored, 12 failed attempts logged, 1417 queued. Setup pending: none.

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
| qwen3:14b | named | 16 | 0.126 [0.106, 0.146] | 0.69 | 0.95 | 0.25 | 0.40 | 1.00 | 0.69 | 0.69 | – |
| qwen3:4b | named | 78 | 0.154 [0.131, 0.176] | 0.31 | 0.81 | 0.38 | 0.27 | 0.78 | 0.81 | 0.28 | 0.35 |
| qwen3:4b | abstract | 60 | 0.202 [0.180, 0.223] | 0.08 | 0.75 | 0.90 | 0.20 | 0.85 | 0.83 | 0.05 | 0.15 |
| gemma3:4b | abstract | 60 | 0.232 [0.206, 0.259] | 0.15 | 0.72 | 0.78 | 0.35 | 0.93 | 0.88 | 0.05 | 0.35 |
| gemma3:4b | named | 105 | 0.245 [0.226, 0.263] | 0.10 | 0.69 | 0.60 | 0.31 | 0.92 | 0.89 | 0.08 | 0.13 |
| mistral:7b | named | 60 | 0.261 [0.228, 0.295] | 0.13 | 0.74 | 0.53 | 0.10 | 0.80 | 0.85 | 0.12 | 0.15 |
| mistral:7b | abstract | 24 | 0.284 [0.246, 0.326] | 0.00 | 0.66 | 0.83 | 0.00 | 0.80 | 0.75 | 0.00 | – |
| llama3.2:3b | abstract | 120 | 0.288 [0.271, 0.305] | 0.03 | 0.62 | 0.67 | 0.12 | 0.79 | 0.62 | 0.05 | 0.00 |
| llama3.2:3b | named | 120 | 0.295 [0.279, 0.310] | 0.03 | 0.61 | 0.80 | 0.33 | 0.72 | 0.63 | 0.04 | 0.03 |

## Results: Axiom-Neuro, semi-synthetic track (real ERP CORE trials)

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| oracle | named | 180 | 0.044 [0.039, 0.049] | 0.77 | 0.96 | 0.03 | 0.18 | 1.00 | 0.77 | 0.75 | 0.80 |
| scripted | named | 180 | 0.049 [0.044, 0.053] | 0.76 | 0.96 | 0.03 | 0.15 | 1.00 | 0.76 | 0.77 | 0.73 |
| random | named | 180 | 0.098 [0.086, 0.111] | 0.57 | 0.91 | 0.14 | 0.08 | 0.69 | 0.57 | 0.54 | 0.62 |
| qwen3:4b | named | 60 | 0.159 [0.134, 0.186] | 0.30 | 0.80 | 0.53 | 0.20 | 0.78 | 0.90 | 0.25 | 0.40 |
| qwen3:4b | abstract | 60 | 0.176 [0.152, 0.197] | 0.15 | 0.78 | 0.73 | 0.00 | 0.82 | 0.90 | 0.15 | 0.15 |
| gemma3:4b | named | 60 | 0.232 [0.210, 0.255] | 0.12 | 0.72 | 0.57 | 0.30 | 0.95 | 0.92 | 0.12 | 0.10 |
| gemma3:4b | abstract | 60 | 0.250 [0.227, 0.276] | 0.10 | 0.69 | 0.78 | 0.50 | 0.97 | 0.95 | 0.05 | 0.20 |
| llama3.2:3b | abstract | 120 | 0.279 [0.266, 0.295] | 0.03 | 0.64 | 0.61 | 0.28 | 0.82 | 0.68 | 0.03 | 0.03 |
| llama3.2:3b | named | 120 | 0.304 [0.288, 0.321] | 0.03 | 0.57 | 0.87 | 0.40 | 0.84 | 0.73 | 0.05 | 0.00 |

## Results: Axiom-Bio (real single cells, Sachs et al. 2005)

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen3:4b | abstract | 40 | 0.255 [0.251, 0.261] | 0.00 | 0.58 | 0.15 | 0.10 | – | 0.00 | 0.00 | – |
| qwen3:4b | named | 40 | 0.257 [0.242, 0.273] | 0.00 | 0.57 | 0.20 | 0.17 | – | 0.00 | 0.00 | – |
| llama3.2:3b | named | 70 | 0.271 [0.255, 0.290] | 0.01 | 0.58 | 0.44 | 0.39 | – | 0.00 | 0.01 | – |
| gemma3:4b | named | 40 | 0.272 [0.252, 0.293] | 0.00 | 0.57 | 0.35 | 0.35 | – | 0.00 | 0.00 | – |
| random | named | 120 | 0.274 [0.260, 0.288] | 0.00 | 0.57 | 1.50 | 0.38 | – | 0.00 | 0.00 | – |
| scripted | named | 120 | 0.276 [0.255, 0.300] | 0.00 | 0.62 | 1.68 | 0.26 | – | 0.00 | 0.00 | – |
| qwen3:14b | abstract | 28 | 0.279 [0.260, 0.300] | 0.00 | 0.55 | 0.57 | 0.64 | – | 0.00 | 0.00 | – |
| llama3.2:3b | abstract | 40 | 0.280 [0.258, 0.306] | 0.00 | 0.57 | 0.53 | 0.42 | – | 0.00 | 0.00 | – |
| gemma3:4b | abstract | 40 | 0.296 [0.275, 0.319] | 0.00 | 0.53 | 0.82 | 0.45 | – | 0.00 | 0.00 | – |
| mistral:7b | named | 22 | 0.298 [0.258, 0.348] | 0.00 | 0.58 | 0.73 | 0.41 | – | 0.00 | 0.00 | – |
| mistral:7b | abstract | 40 | 0.308 [0.277, 0.345] | 0.00 | 0.55 | 0.78 | 0.33 | – | 0.00 | 0.00 | – |

## Preregistered hypotheses (see PREREGISTRATION.md)

- **H1** (evaluated): 5/5 models' Brier CI lies wholly above (worse than) the scripted baseline (0.050).
- **H2** (evaluated): llama3.2:3b: trap 0.33 vs mirror denial 0.57, Holm p = 1; qwen3:4b: trap 0.27 vs mirror denial 0.15, Holm p = 1; gemma3:4b: trap 0.31 vs mirror denial 0.40, Holm p = 1; mistral:7b: trap 0.10 vs mirror denial 0.50, Holm p = 1
- **H3** (evaluated): llama3.2:3b: own claims 0.03 vs ideal analysis of its data 0.63; qwen3:4b: own claims 0.31 vs ideal analysis of its data 0.81; gemma3:4b: own claims 0.10 vs ideal analysis of its data 0.89; mistral:7b: own claims 0.13 vs ideal analysis of its data 0.85; qwen3:14b: own claims 0.69 vs ideal analysis of its data 0.69
- **H4** (evaluated): Spearman rho(size, Brier) = -0.60 (negative = bigger is better; n = 5, p = 0.285)
- **H5** (evaluated): Kendall tau synthetic vs semi-synthetic agent ranking = 1.00 (n = 6)
- **H6** (evaluated): llama3.2:3b: Brier abstract - named = -0.007 (positive = names help); qwen3:4b: Brier abstract - named = +0.047 (positive = names help); gemma3:4b: Brier abstract - named = -0.013 (positive = names help); mistral:7b: Brier abstract - named = +0.024 (positive = names help)
- **B1** (evaluated): llama3.2:3b: Brier abstract - named = +0.009 over 40 tasks, Holm p = 0.551; qwen3:4b: Brier abstract - named = -0.001 over 40 tasks, Holm p = 0.811; gemma3:4b: Brier abstract - named = +0.024 over 40 tasks, Holm p = 0.213; mistral:7b: Brier abstract - named = +0.019 over 22 tasks, Holm p = 0.811
- **B2** (evaluated): llama3.2:3b: Brier model - reference = +0.004 [-0.027, +0.034]; qwen3:4b: Brier model - reference = -0.021 [-0.045, +0.002]; gemma3:4b: Brier model - reference = +0.020 [-0.010, +0.048]; mistral:7b: Brier model - reference = +0.032 [-0.007, +0.073]; qwen3:14b: Brier model - reference = -0.001 [-0.034, +0.030]
- **B3** (evaluated): llama3.2:3b: claims true 0.20 / reversed 0.12 / indirect 0.18 / confounded 0.12; qwen3:4b: claims true 0.09 / reversed 0.11 / indirect 0.02 / confounded 0.06; gemma3:4b: claims true 0.31 / reversed 0.22 / indirect 0.20 / confounded 0.29; mistral:7b: claims true 0.24 / reversed 0.27 / indirect 0.17 / confounded 0.11

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
