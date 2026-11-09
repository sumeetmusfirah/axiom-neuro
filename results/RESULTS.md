# Axiom-Neuro results

Auto-generated from `results/ledger.jsonl` (data as of 2026-11-09T05:09:36.769120+00:00). Do not edit by hand.

**Progress:** 6633 episodes scored, 142 failed attempts logged, 3019 queued. Setup pending: none.

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
| qwen3.5:9b † | abstract | 60 | 0.085 [0.065, 0.108] | 0.62 | 0.91 | 0.20 | 0.20 | 0.80 | 0.73 | 0.55 | 0.75 |
| gemma4:e4b † | named | 60 | 0.092 [0.074, 0.111] | 0.53 | 0.90 | 0.32 | 0.40 | 0.95 | 0.80 | 0.50 | 0.60 |
| qwen3.5:9b † | named | 60 | 0.095 [0.072, 0.119] | 0.60 | 0.91 | 0.23 | 0.45 | 0.72 | 0.67 | 0.55 | 0.70 |
| random | named | 180 | 0.120 [0.107, 0.134] | 0.46 | 0.87 | 0.32 | 0.08 | 0.69 | 0.46 | 0.49 | 0.38 |
| qwen3:14b | named | 60 | 0.127 [0.117, 0.137] | 0.80 | 0.96 | 0.13 | 0.20 | 1.00 | 0.80 | 0.80 | 0.80 |
| gemma4:e4b † | abstract | 60 | 0.140 [0.121, 0.161] | 0.23 | 0.84 | 0.43 | 0.35 | 0.95 | 0.78 | 0.17 | 0.35 |
| qwen3:14b | abstract | 60 | 0.161 [0.149, 0.172] | 0.35 | 0.87 | 0.18 | 0.40 | 0.95 | 0.80 | 0.30 | 0.45 |
| qwen3:4b | named | 180 | 0.170 [0.154, 0.185] | 0.24 | 0.80 | 0.54 | 0.25 | 0.74 | 0.76 | 0.23 | 0.27 |
| qwen3:4b | abstract | 172 | 0.183 [0.165, 0.201] | 0.14 | 0.77 | 0.89 | 0.12 | 0.74 | 0.81 | 0.10 | 0.17 |
| gemma3:4b | abstract | 180 | 0.239 [0.222, 0.255] | 0.12 | 0.71 | 0.74 | 0.40 | 0.91 | 0.86 | 0.05 | 0.27 |
| gemma3:4b | named | 180 | 0.243 [0.229, 0.256] | 0.12 | 0.71 | 0.58 | 0.30 | 0.95 | 0.85 | 0.09 | 0.17 |
| mistral:7b | named | 120 | 0.259 [0.237, 0.280] | 0.12 | 0.72 | 0.61 | 0.17 | 0.80 | 0.85 | 0.11 | 0.12 |
| mistral:7b | abstract | 101 | 0.276 [0.249, 0.303] | 0.04 | 0.69 | 0.91 | 0.16 | 0.82 | 0.83 | 0.04 | 0.03 |
| llama3.2:3b | abstract | 240 | 0.282 [0.269, 0.293] | 0.03 | 0.63 | 0.64 | 0.20 | 0.77 | 0.62 | 0.04 | 0.00 |
| llama3.2:3b | named | 240 | 0.302 [0.290, 0.316] | 0.03 | 0.59 | 0.85 | 0.34 | 0.74 | 0.66 | 0.03 | 0.01 |

## Results: Axiom-Neuro, semi-synthetic track (real ERP CORE trials)

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| oracle | named | 180 | 0.044 [0.039, 0.049] | 0.77 | 0.96 | 0.03 | 0.18 | 1.00 | 0.77 | 0.75 | 0.80 |
| scripted | named | 180 | 0.049 [0.044, 0.053] | 0.76 | 0.96 | 0.03 | 0.15 | 1.00 | 0.76 | 0.77 | 0.73 |
| gemma4:e4b † | named | 60 | 0.069 [0.054, 0.085] | 0.58 | 0.92 | 0.23 | 0.35 | 0.95 | 0.73 | 0.60 | 0.55 |
| qwen3.5:9b † | named | 40 | 0.078 [0.049, 0.110] | 0.70 | 0.91 | 0.10 | 0.50 | 0.30 | 0.85 | 0.70 | 0.70 |
| random | named | 180 | 0.098 [0.086, 0.111] | 0.57 | 0.91 | 0.14 | 0.08 | 0.69 | 0.57 | 0.54 | 0.62 |
| gemma4:e4b † | abstract | 54 | 0.114 [0.095, 0.133] | 0.39 | 0.87 | 0.30 | 0.15 | 0.94 | 0.83 | 0.38 | 0.43 |
| qwen3:14b | named | 18 | 0.134 [0.115, 0.155] | 0.61 | 0.94 | 0.28 | 0.40 | 0.90 | 0.67 | 0.61 | – |
| qwen3:4b | named | 120 | 0.161 [0.141, 0.183] | 0.28 | 0.78 | 0.47 | 0.17 | 0.70 | 0.80 | 0.24 | 0.35 |
| qwen3:4b | abstract | 120 | 0.179 [0.157, 0.199] | 0.16 | 0.78 | 0.82 | 0.05 | 0.81 | 0.83 | 0.16 | 0.15 |
| gemma3:4b | named | 180 | 0.226 [0.215, 0.238] | 0.12 | 0.73 | 0.43 | 0.18 | 0.94 | 0.86 | 0.12 | 0.13 |
| gemma3:4b | abstract | 180 | 0.250 [0.236, 0.263] | 0.10 | 0.68 | 0.76 | 0.43 | 0.97 | 0.89 | 0.07 | 0.17 |
| mistral:7b | abstract | 60 | 0.266 [0.240, 0.295] | 0.10 | 0.69 | 0.72 | 0.20 | 0.68 | 0.93 | 0.10 | 0.10 |
| mistral:7b | named | 60 | 0.268 [0.233, 0.307] | 0.10 | 0.74 | 0.52 | 0.00 | 0.80 | 0.80 | 0.10 | 0.10 |
| llama3.2:3b | abstract | 240 | 0.285 [0.272, 0.299] | 0.03 | 0.63 | 0.68 | 0.26 | 0.84 | 0.66 | 0.03 | 0.01 |
| llama3.2:3b | named | 240 | 0.303 [0.290, 0.318] | 0.03 | 0.59 | 0.86 | 0.40 | 0.82 | 0.74 | 0.04 | 0.00 |

## Results: Axiom-Bio (real single cells, Sachs et al. 2005)

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen3:4b | abstract | 80 | 0.251 [0.248, 0.255] | 0.00 | 0.59 | 0.07 | 0.05 | – | 0.00 | 0.00 | – |
| qwen3:4b | named | 80 | 0.253 [0.245, 0.262] | 0.00 | 0.58 | 0.15 | 0.15 | – | 0.00 | 0.00 | – |
| gemma3:4b | named | 120 | 0.274 [0.260, 0.289] | 0.00 | 0.58 | 0.49 | 0.34 | – | 0.00 | 0.00 | – |
| random | named | 120 | 0.274 [0.260, 0.288] | 0.00 | 0.57 | 1.50 | 0.38 | – | 0.00 | 0.00 | – |
| scripted | named | 120 | 0.276 [0.255, 0.300] | 0.00 | 0.62 | 1.68 | 0.26 | – | 0.00 | 0.00 | – |
| llama3.2:3b | named | 160 | 0.277 [0.264, 0.290] | 0.01 | 0.57 | 0.46 | 0.39 | – | 0.00 | 0.01 | – |
| qwen3:14b | abstract | 28 | 0.279 [0.260, 0.300] | 0.00 | 0.55 | 0.57 | 0.64 | – | 0.00 | 0.00 | – |
| gemma3:4b | abstract | 85 | 0.281 [0.265, 0.297] | 0.00 | 0.57 | 0.60 | 0.45 | – | 0.00 | 0.00 | – |
| llama3.2:3b | abstract | 160 | 0.285 [0.272, 0.298] | 0.01 | 0.57 | 0.59 | 0.43 | – | 0.00 | 0.01 | – |
| mistral:7b | named | 40 | 0.307 [0.275, 0.350] | 0.00 | 0.56 | 0.75 | 0.38 | – | 0.00 | 0.00 | – |
| mistral:7b | abstract | 40 | 0.308 [0.277, 0.345] | 0.00 | 0.55 | 0.78 | 0.33 | – | 0.00 | 0.00 | – |

## Results: Axiom-Health (exploratory; real NHANES 2017-18 adults, planted exposure)

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| scripted | named | 60 | 0.018 [0.011, 0.027] | 0.88 | 0.98 | 0.02 | 0.02 | – | 0.88 | 0.88 | – |
| random | named | 60 | 0.061 [0.041, 0.083] | 0.55 | 0.91 | 0.18 | 0.25 | – | 0.55 | 0.55 | – |
| qwen3:4b | named | 40 | 0.239 [0.233, 0.246] | 0.05 | 0.41 | 0.07 | 0.25 | – | 0.47 | 0.05 | – |
| qwen3:4b | abstract | 40 | 0.244 [0.235, 0.252] | 0.05 | 0.42 | 0.12 | 0.25 | – | 0.50 | 0.05 | – |
| llama3.2:3b | abstract | 80 | 0.248 [0.228, 0.268] | 0.03 | 0.48 | 0.50 | 0.33 | – | 0.40 | 0.03 | – |
| mistral:7b | abstract | 20 | 0.261 [0.238, 0.286] | 0.00 | 0.36 | 0.20 | 0.40 | – | 0.30 | 0.00 | – |
| llama3.2:3b | named | 80 | 0.270 [0.247, 0.296] | 0.03 | 0.44 | 0.56 | 0.38 | – | 0.40 | 0.03 | – |
| gemma3:4b | named | 40 | 0.273 [0.239, 0.316] | 0.05 | 0.45 | 0.68 | 0.40 | – | 0.35 | 0.05 | – |
| mistral:7b | named | 20 | 0.284 [0.242, 0.334] | 0.05 | 0.40 | 0.45 | 0.40 | – | 0.35 | 0.05 | – |
| gemma3:4b | abstract | 40 | 0.292 [0.257, 0.326] | 0.00 | 0.38 | 0.75 | 0.47 | – | 0.45 | 0.00 | – |

## Results: Axiom-Ethics (exploratory; real COMPAS risk scores, ProPublica)

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| scripted | named | 60 | 0.014 [0.009, 0.019] | 0.93 | 0.99 | 0.00 | 0.00 | – | 0.93 | 0.93 | – |
| random | named | 60 | 0.130 [0.102, 0.160] | 0.40 | 0.84 | 0.60 | 0.32 | – | 0.40 | 0.40 | – |
| qwen3:4b | named | 40 | 0.222 [0.194, 0.243] | 0.10 | 0.53 | 0.03 | 0.70 | – | 0.65 | 0.10 | – |
| qwen3:4b | abstract | 40 | 0.243 [0.235, 0.249] | 0.00 | 0.48 | 0.05 | 0.80 | – | 0.45 | 0.00 | – |
| mistral:7b | named | 20 | 0.258 [0.239, 0.281] | 0.00 | 0.51 | 0.10 | 0.75 | – | 0.50 | 0.00 | – |
| mistral:7b | abstract | 20 | 0.283 [0.248, 0.330] | 0.00 | 0.50 | 0.45 | 0.65 | – | 0.35 | 0.00 | – |
| gemma3:4b | abstract | 40 | 0.285 [0.260, 0.311] | 0.00 | 0.46 | 0.60 | 0.72 | – | 0.42 | 0.00 | – |
| llama3.2:3b | abstract | 78 | 0.295 [0.271, 0.322] | 0.00 | 0.49 | 0.87 | 0.76 | – | 0.50 | 0.00 | – |
| gemma3:4b | named | 40 | 0.297 [0.260, 0.343] | 0.00 | 0.52 | 1.00 | 0.68 | – | 0.40 | 0.00 | – |
| llama3.2:3b | named | 80 | 0.301 [0.274, 0.329] | 0.00 | 0.51 | 0.82 | 0.72 | – | 0.31 | 0.00 | – |

† Added after preregistration by model intake or as a hosted model (see `configs/experiment.toml`, `[intake]` and `[hosted]`). Reported, but excluded from the preregistered tests.

## Preregistered hypotheses (see PREREGISTRATION.md)

- **H1** (evaluated): 5/5 models' Brier CI lies wholly above (worse than) the scripted baseline (0.050).
- **H2** (evaluated): llama3.2:3b: trap 0.34 vs mirror denial 0.65, Holm p = 1; qwen3:4b: trap 0.25 vs mirror denial 0.32, Holm p = 1; gemma3:4b: trap 0.30 vs mirror denial 0.35, Holm p = 1; mistral:7b: trap 0.17 vs mirror denial 0.55, Holm p = 1; qwen3:14b: trap 0.20 vs mirror denial 0.10, Holm p = 1
- **H3** (evaluated): llama3.2:3b: own claims 0.03 vs ideal analysis of its data 0.66; qwen3:4b: own claims 0.24 vs ideal analysis of its data 0.76; gemma3:4b: own claims 0.12 vs ideal analysis of its data 0.85; mistral:7b: own claims 0.12 vs ideal analysis of its data 0.85; qwen3:14b: own claims 0.80 vs ideal analysis of its data 0.80
- **H4** (evaluated): Spearman rho(size, Brier) = -0.60 (negative = bigger is better; n = 5, p = 0.285)
- **H5** (evaluated): Kendall tau synthetic vs semi-synthetic agent ranking = 1.00 (n = 8)
- **H6** (evaluated): llama3.2:3b: Brier abstract - named = -0.020 (positive = names help); qwen3:4b: Brier abstract - named = +0.013 (positive = names help); gemma3:4b: Brier abstract - named = -0.004 (positive = names help); mistral:7b: Brier abstract - named = +0.017 (positive = names help); qwen3:14b: Brier abstract - named = +0.034 (positive = names help)
- **B1** (evaluated): llama3.2:3b: Brier abstract - named = +0.008 over 40 tasks, Holm p = 1; qwen3:4b: Brier abstract - named = -0.002 over 40 tasks, Holm p = 1; gemma3:4b: Brier abstract - named = +0.006 over 40 tasks, Holm p = 1; mistral:7b: Brier abstract - named = +0.001 over 40 tasks, Holm p = 1
- **B2** (evaluated): llama3.2:3b: Brier model - reference = +0.008 [-0.020, +0.035]; qwen3:4b: Brier model - reference = -0.025 [-0.049, -0.002]; gemma3:4b: Brier model - reference = +0.004 [-0.023, +0.030]; mistral:7b: Brier model - reference = +0.032 [-0.007, +0.073]; qwen3:14b: Brier model - reference = -0.001 [-0.034, +0.030]
- **B3** (evaluated): llama3.2:3b: claims true 0.17 / reversed 0.13 / indirect 0.17 / confounded 0.13; qwen3:4b: claims true 0.08 / reversed 0.09 / indirect 0.03 / confounded 0.04; gemma3:4b: claims true 0.28 / reversed 0.22 / indirect 0.15 / confounded 0.22; mistral:7b: claims true 0.20 / reversed 0.22 / indirect 0.16 / confounded 0.15

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
