# Axiom-Neuro results

Auto-generated from `results/ledger.jsonl` (data as of 2026-11-07T12:33:00.714729+00:00). Do not edit by hand.

**Progress:** 5492 episodes scored, 115 failed attempts logged, 3142 queued. Setup pending: none.

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
| gemma4:e4b † | named | 60 | 0.092 [0.074, 0.111] | 0.53 | 0.90 | 0.32 | 0.40 | 0.95 | 0.80 | 0.50 | 0.60 |
| qwen3.5:9b † | named | 50 | 0.104 [0.078, 0.131] | 0.58 | 0.90 | 0.26 | 0.45 | 0.63 | 0.66 | 0.55 | 0.70 |
| random | named | 180 | 0.120 [0.107, 0.134] | 0.46 | 0.87 | 0.32 | 0.08 | 0.69 | 0.46 | 0.49 | 0.38 |
| qwen3:14b | named | 60 | 0.127 [0.117, 0.137] | 0.80 | 0.96 | 0.13 | 0.20 | 1.00 | 0.80 | 0.80 | 0.80 |
| gemma4:e4b † | abstract | 60 | 0.140 [0.121, 0.161] | 0.23 | 0.84 | 0.43 | 0.35 | 0.95 | 0.78 | 0.17 | 0.35 |
| qwen3:4b | named | 120 | 0.165 [0.147, 0.181] | 0.28 | 0.80 | 0.42 | 0.25 | 0.79 | 0.79 | 0.26 | 0.30 |
| qwen3:4b | abstract | 120 | 0.190 [0.171, 0.210] | 0.12 | 0.76 | 0.89 | 0.15 | 0.78 | 0.82 | 0.07 | 0.20 |
| qwen3:14b | abstract | 8 | 0.222 [0.197, 0.251] | 0.00 | 0.75 | 0.88 | 0.88 | 1.00 | 0.50 | 0.00 | – |
| gemma3:4b | abstract | 120 | 0.231 [0.213, 0.249] | 0.11 | 0.72 | 0.71 | 0.38 | 0.90 | 0.88 | 0.03 | 0.28 |
| gemma3:4b | named | 180 | 0.243 [0.229, 0.256] | 0.12 | 0.71 | 0.58 | 0.30 | 0.95 | 0.85 | 0.09 | 0.17 |
| mistral:7b | named | 60 | 0.261 [0.228, 0.295] | 0.13 | 0.74 | 0.53 | 0.10 | 0.80 | 0.85 | 0.12 | 0.15 |
| mistral:7b | abstract | 60 | 0.277 [0.250, 0.305] | 0.02 | 0.69 | 0.88 | 0.20 | 0.90 | 0.83 | 0.00 | 0.05 |
| llama3.2:3b | abstract | 203 | 0.284 [0.270, 0.297] | 0.03 | 0.63 | 0.64 | 0.19 | 0.77 | 0.63 | 0.05 | 0.00 |
| llama3.2:3b | named | 240 | 0.302 [0.290, 0.316] | 0.03 | 0.59 | 0.85 | 0.34 | 0.74 | 0.66 | 0.03 | 0.01 |

## Results: Axiom-Neuro, semi-synthetic track (real ERP CORE trials)

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| oracle | named | 180 | 0.044 [0.039, 0.049] | 0.77 | 0.96 | 0.03 | 0.18 | 1.00 | 0.77 | 0.75 | 0.80 |
| scripted | named | 180 | 0.049 [0.044, 0.053] | 0.76 | 0.96 | 0.03 | 0.15 | 1.00 | 0.76 | 0.77 | 0.73 |
| random | named | 180 | 0.098 [0.086, 0.111] | 0.57 | 0.91 | 0.14 | 0.08 | 0.69 | 0.57 | 0.54 | 0.62 |
| gemma4:e4b † | named | 10 | 0.123 [0.087, 0.156] | 0.20 | 0.85 | 0.60 | 0.70 | 0.80 | 0.70 | 0.20 | – |
| qwen3:4b | named | 120 | 0.161 [0.141, 0.183] | 0.28 | 0.78 | 0.47 | 0.17 | 0.70 | 0.80 | 0.24 | 0.35 |
| qwen3:4b | abstract | 120 | 0.179 [0.157, 0.199] | 0.16 | 0.78 | 0.82 | 0.05 | 0.81 | 0.83 | 0.16 | 0.15 |
| gemma3:4b | named | 120 | 0.227 [0.212, 0.242] | 0.12 | 0.73 | 0.42 | 0.17 | 0.93 | 0.85 | 0.11 | 0.15 |
| gemma3:4b | abstract | 120 | 0.258 [0.240, 0.275] | 0.08 | 0.67 | 0.81 | 0.50 | 0.97 | 0.89 | 0.04 | 0.17 |
| mistral:7b | abstract | 60 | 0.266 [0.240, 0.295] | 0.10 | 0.69 | 0.72 | 0.20 | 0.68 | 0.93 | 0.10 | 0.10 |
| mistral:7b | named | 60 | 0.268 [0.233, 0.307] | 0.10 | 0.74 | 0.52 | 0.00 | 0.80 | 0.80 | 0.10 | 0.10 |
| llama3.2:3b | abstract | 180 | 0.284 [0.270, 0.301] | 0.02 | 0.63 | 0.65 | 0.25 | 0.83 | 0.66 | 0.02 | 0.02 |
| llama3.2:3b | named | 180 | 0.301 [0.286, 0.317] | 0.03 | 0.59 | 0.87 | 0.40 | 0.78 | 0.72 | 0.05 | 0.00 |

## Results: Axiom-Bio (real single cells, Sachs et al. 2005)

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen3:4b | abstract | 80 | 0.251 [0.248, 0.255] | 0.00 | 0.59 | 0.07 | 0.05 | – | 0.00 | 0.00 | – |
| qwen3:4b | named | 80 | 0.253 [0.245, 0.262] | 0.00 | 0.58 | 0.15 | 0.15 | – | 0.00 | 0.00 | – |
| random | named | 120 | 0.274 [0.260, 0.288] | 0.00 | 0.57 | 1.50 | 0.38 | – | 0.00 | 0.00 | – |
| scripted | named | 120 | 0.276 [0.255, 0.300] | 0.00 | 0.62 | 1.68 | 0.26 | – | 0.00 | 0.00 | – |
| gemma3:4b | named | 80 | 0.277 [0.261, 0.295] | 0.00 | 0.58 | 0.53 | 0.35 | – | 0.00 | 0.00 | – |
| llama3.2:3b | named | 120 | 0.278 [0.265, 0.292] | 0.01 | 0.57 | 0.47 | 0.41 | – | 0.00 | 0.01 | – |
| qwen3:14b | abstract | 28 | 0.279 [0.260, 0.300] | 0.00 | 0.55 | 0.57 | 0.64 | – | 0.00 | 0.00 | – |
| gemma3:4b | abstract | 80 | 0.280 [0.264, 0.297] | 0.00 | 0.58 | 0.60 | 0.42 | – | 0.00 | 0.00 | – |
| llama3.2:3b | abstract | 120 | 0.283 [0.267, 0.302] | 0.01 | 0.57 | 0.58 | 0.42 | – | 0.00 | 0.01 | – |
| mistral:7b | named | 40 | 0.307 [0.275, 0.350] | 0.00 | 0.56 | 0.75 | 0.38 | – | 0.00 | 0.00 | – |
| mistral:7b | abstract | 40 | 0.308 [0.277, 0.345] | 0.00 | 0.55 | 0.78 | 0.33 | – | 0.00 | 0.00 | – |

## Results: Axiom-Health (exploratory; real NHANES 2017-18 adults, planted exposure)

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| scripted | named | 60 | 0.018 [0.011, 0.027] | 0.88 | 0.98 | 0.02 | 0.02 | – | 0.88 | 0.88 | – |
| random | named | 60 | 0.061 [0.041, 0.083] | 0.55 | 0.91 | 0.18 | 0.25 | – | 0.55 | 0.55 | – |
| qwen3:4b | abstract | 20 | 0.242 [0.225, 0.256] | 0.05 | 0.42 | 0.10 | 0.25 | – | 0.55 | 0.05 | – |
| qwen3:4b | named | 27 | 0.245 [0.236, 0.253] | 0.05 | 0.38 | 0.07 | 0.22 | – | 0.48 | 0.04 | – |
| llama3.2:3b | abstract | 60 | 0.248 [0.227, 0.269] | 0.03 | 0.48 | 0.52 | 0.32 | – | 0.42 | 0.03 | – |
| mistral:7b | abstract | 20 | 0.261 [0.238, 0.286] | 0.00 | 0.36 | 0.20 | 0.40 | – | 0.30 | 0.00 | – |
| llama3.2:3b | named | 60 | 0.265 [0.248, 0.285] | 0.03 | 0.43 | 0.50 | 0.37 | – | 0.45 | 0.03 | – |
| gemma3:4b | named | 40 | 0.273 [0.239, 0.316] | 0.05 | 0.45 | 0.68 | 0.40 | – | 0.35 | 0.05 | – |
| mistral:7b | named | 20 | 0.284 [0.242, 0.334] | 0.05 | 0.40 | 0.45 | 0.40 | – | 0.35 | 0.05 | – |
| gemma3:4b | abstract | 40 | 0.292 [0.257, 0.326] | 0.00 | 0.38 | 0.75 | 0.47 | – | 0.45 | 0.00 | – |

## Results: Axiom-Ethics (exploratory; real COMPAS risk scores, ProPublica)

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| scripted | named | 60 | 0.014 [0.009, 0.019] | 0.93 | 0.99 | 0.00 | 0.00 | – | 0.93 | 0.93 | – |
| random | named | 60 | 0.130 [0.102, 0.160] | 0.40 | 0.84 | 0.60 | 0.32 | – | 0.40 | 0.40 | – |
| qwen3:4b | named | 20 | 0.221 [0.187, 0.246] | 0.10 | 0.52 | 0.00 | 0.65 | – | 0.75 | 0.10 | – |
| qwen3:4b | abstract | 20 | 0.250 [0.250, 0.250] | 0.00 | 0.47 | 0.00 | 0.80 | – | 0.50 | 0.00 | – |
| mistral:7b | named | 16 | 0.260 [0.236, 0.289] | 0.00 | 0.49 | 0.12 | 0.81 | – | 0.44 | 0.00 | – |
| gemma3:4b | abstract | 40 | 0.285 [0.260, 0.311] | 0.00 | 0.46 | 0.60 | 0.72 | – | 0.42 | 0.00 | – |
| llama3.2:3b | named | 60 | 0.291 [0.268, 0.316] | 0.00 | 0.51 | 0.77 | 0.67 | – | 0.30 | 0.00 | – |
| llama3.2:3b | abstract | 60 | 0.296 [0.273, 0.320] | 0.00 | 0.49 | 0.87 | 0.73 | – | 0.47 | 0.00 | – |
| gemma3:4b | named | 40 | 0.297 [0.260, 0.343] | 0.00 | 0.52 | 1.00 | 0.68 | – | 0.40 | 0.00 | – |

† Added after preregistration by model intake or as a hosted model (see `configs/experiment.toml`, `[intake]` and `[hosted]`). Reported, but excluded from the preregistered tests.

## Preregistered hypotheses (see PREREGISTRATION.md)

- **H1** (evaluated): 5/5 models' Brier CI lies wholly above (worse than) the scripted baseline (0.050).
- **H2** (evaluated): llama3.2:3b: trap 0.34 vs mirror denial 0.65, Holm p = 1; qwen3:4b: trap 0.25 vs mirror denial 0.30, Holm p = 1; gemma3:4b: trap 0.30 vs mirror denial 0.35, Holm p = 1; mistral:7b: trap 0.10 vs mirror denial 0.50, Holm p = 1; qwen3:14b: trap 0.20 vs mirror denial 0.10, Holm p = 1
- **H3** (evaluated): llama3.2:3b: own claims 0.03 vs ideal analysis of its data 0.66; qwen3:4b: own claims 0.28 vs ideal analysis of its data 0.79; gemma3:4b: own claims 0.12 vs ideal analysis of its data 0.85; mistral:7b: own claims 0.13 vs ideal analysis of its data 0.85; qwen3:14b: own claims 0.80 vs ideal analysis of its data 0.80
- **H4** (evaluated): Spearman rho(size, Brier) = -0.60 (negative = bigger is better; n = 5, p = 0.285)
- **H5** (evaluated): Kendall tau synthetic vs semi-synthetic agent ranking = 1.00 (n = 7)
- **H6** (evaluated): llama3.2:3b: Brier abstract - named = -0.018 (positive = names help); qwen3:4b: Brier abstract - named = +0.026 (positive = names help); gemma3:4b: Brier abstract - named = -0.012 (positive = names help); mistral:7b: Brier abstract - named = +0.016 (positive = names help); qwen3:14b: Brier abstract - named = +0.095 (positive = names help)
- **B1** (evaluated): llama3.2:3b: Brier abstract - named = +0.005 over 40 tasks, Holm p = 1; qwen3:4b: Brier abstract - named = -0.002 over 40 tasks, Holm p = 1; gemma3:4b: Brier abstract - named = +0.003 over 40 tasks, Holm p = 1; mistral:7b: Brier abstract - named = +0.001 over 40 tasks, Holm p = 1
- **B2** (evaluated): llama3.2:3b: Brier model - reference = +0.006 [-0.023, +0.035]; qwen3:4b: Brier model - reference = -0.025 [-0.049, -0.002]; gemma3:4b: Brier model - reference = +0.004 [-0.023, +0.029]; mistral:7b: Brier model - reference = +0.032 [-0.007, +0.073]; qwen3:14b: Brier model - reference = -0.001 [-0.034, +0.030]
- **B3** (evaluated): llama3.2:3b: claims true 0.17 / reversed 0.12 / indirect 0.18 / confounded 0.13; qwen3:4b: claims true 0.08 / reversed 0.09 / indirect 0.03 / confounded 0.04; gemma3:4b: claims true 0.30 / reversed 0.23 / indirect 0.17 / confounded 0.25; mistral:7b: claims true 0.20 / reversed 0.22 / indirect 0.16 / confounded 0.15

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
