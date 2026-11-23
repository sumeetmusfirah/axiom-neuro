# Axiom-Neuro results

Auto-generated from `results/ledger.jsonl` (data as of 2026-11-23T14:56:29.075373+00:00). Do not edit by hand.

**Progress:** 13963 episodes scored, 262 failed attempts logged, 1564 queued. Setup pending: none.

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
| qwen3.5:9b † | abstract | 180 | 0.081 [0.069, 0.093] | 0.64 | 0.92 | 0.20 | 0.27 | 0.78 | 0.74 | 0.59 | 0.75 |
| gemma4:e4b † | named | 180 | 0.090 [0.076, 0.105] | 0.54 | 0.90 | 0.33 | 0.38 | 0.95 | 0.77 | 0.48 | 0.65 |
| qwen3.5:9b † | named | 180 | 0.091 [0.077, 0.105] | 0.58 | 0.90 | 0.27 | 0.40 | 0.69 | 0.74 | 0.53 | 0.67 |
| random | named | 180 | 0.120 [0.107, 0.134] | 0.46 | 0.87 | 0.32 | 0.08 | 0.69 | 0.46 | 0.49 | 0.38 |
| gemma4:e4b † | abstract | 180 | 0.135 [0.122, 0.147] | 0.28 | 0.84 | 0.42 | 0.38 | 0.97 | 0.76 | 0.25 | 0.33 |
| qwen3:14b | named | 120 | 0.138 [0.129, 0.147] | 0.69 | 0.94 | 0.18 | 0.28 | 0.97 | 0.81 | 0.65 | 0.78 |
| qwen3:14b | abstract | 120 | 0.152 [0.144, 0.161] | 0.47 | 0.89 | 0.12 | 0.30 | 0.97 | 0.82 | 0.44 | 0.55 |
| qwen3:4b | named | 420 | 0.176 [0.165, 0.187] | 0.22 | 0.79 | 0.55 | 0.29 | 0.77 | 0.79 | 0.20 | 0.28 |
| qwen3:4b | abstract | 381 | 0.185 [0.170, 0.200] | 0.14 | 0.77 | 0.83 | 0.13 | 0.75 | 0.81 | 0.12 | 0.17 |
| gemma3:4b | abstract | 420 | 0.242 [0.231, 0.252] | 0.11 | 0.70 | 0.75 | 0.41 | 0.94 | 0.85 | 0.06 | 0.21 |
| gemma3:4b | named | 290 | 0.242 [0.231, 0.253] | 0.12 | 0.71 | 0.56 | 0.28 | 0.94 | 0.83 | 0.10 | 0.14 |
| mistral:7b | named | 300 | 0.252 [0.239, 0.265] | 0.16 | 0.73 | 0.63 | 0.17 | 0.86 | 0.85 | 0.18 | 0.12 |
| mistral:7b | abstract | 251 | 0.271 [0.254, 0.289] | 0.05 | 0.70 | 0.86 | 0.09 | 0.84 | 0.83 | 0.03 | 0.09 |
| llama3.2:3b | abstract | 300 | 0.282 [0.271, 0.292] | 0.02 | 0.63 | 0.63 | 0.22 | 0.78 | 0.65 | 0.04 | 0.00 |
| llama3.2:3b | named | 360 | 0.298 [0.287, 0.309] | 0.02 | 0.59 | 0.81 | 0.26 | 0.72 | 0.66 | 0.03 | 0.01 |

## Results: Axiom-Neuro, semi-synthetic track (real ERP CORE trials)

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| oracle | named | 180 | 0.044 [0.039, 0.049] | 0.77 | 0.96 | 0.03 | 0.18 | 1.00 | 0.77 | 0.75 | 0.80 |
| scripted | named | 180 | 0.049 [0.044, 0.053] | 0.76 | 0.96 | 0.03 | 0.15 | 1.00 | 0.76 | 0.77 | 0.73 |
| gemma4:e4b † | named | 180 | 0.077 [0.066, 0.088] | 0.58 | 0.91 | 0.31 | 0.38 | 0.97 | 0.73 | 0.57 | 0.58 |
| qwen3.5:9b † | abstract | 127 | 0.081 [0.065, 0.098] | 0.61 | 0.90 | 0.23 | 0.13 | 0.79 | 0.69 | 0.63 | 0.53 |
| qwen3.5:9b † | named | 180 | 0.085 [0.070, 0.102] | 0.66 | 0.91 | 0.13 | 0.20 | 0.68 | 0.73 | 0.62 | 0.73 |
| random | named | 180 | 0.098 [0.086, 0.111] | 0.57 | 0.91 | 0.14 | 0.08 | 0.69 | 0.57 | 0.54 | 0.62 |
| qwen3:14b | named | 120 | 0.121 [0.113, 0.129] | 0.80 | 0.97 | 0.06 | 0.12 | 0.99 | 0.80 | 0.80 | 0.80 |
| gemma4:e4b † | abstract | 180 | 0.128 [0.117, 0.140] | 0.33 | 0.85 | 0.38 | 0.25 | 0.97 | 0.78 | 0.32 | 0.37 |
| qwen3:14b | abstract | 120 | 0.146 [0.139, 0.153] | 0.42 | 0.89 | 0.04 | 0.00 | 0.97 | 0.85 | 0.42 | 0.42 |
| qwen3:4b | named | 420 | 0.164 [0.153, 0.175] | 0.26 | 0.79 | 0.47 | 0.18 | 0.70 | 0.79 | 0.24 | 0.30 |
| qwen3:4b | abstract | 360 | 0.180 [0.162, 0.198] | 0.13 | 0.77 | 0.77 | 0.07 | 0.78 | 0.85 | 0.12 | 0.15 |
| gemma3:4b | named | 215 | 0.228 [0.218, 0.239] | 0.11 | 0.72 | 0.47 | 0.20 | 0.94 | 0.84 | 0.10 | 0.12 |
| gemma3:4b | abstract | 360 | 0.246 [0.236, 0.254] | 0.09 | 0.70 | 0.74 | 0.35 | 0.98 | 0.88 | 0.06 | 0.15 |
| mistral:7b | named | 240 | 0.256 [0.240, 0.273] | 0.17 | 0.74 | 0.59 | 0.14 | 0.84 | 0.80 | 0.19 | 0.15 |
| mistral:7b | abstract | 240 | 0.260 [0.245, 0.275] | 0.10 | 0.70 | 0.67 | 0.16 | 0.77 | 0.84 | 0.10 | 0.11 |
| llama3.2:3b | abstract | 300 | 0.282 [0.271, 0.294] | 0.02 | 0.63 | 0.64 | 0.23 | 0.82 | 0.68 | 0.03 | 0.01 |
| llama3.2:3b | named | 420 | 0.302 [0.292, 0.311] | 0.02 | 0.59 | 0.84 | 0.32 | 0.82 | 0.70 | 0.03 | 0.00 |

## Results: Axiom-Bio (real single cells, Sachs et al. 2005)

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen3:4b | abstract | 120 | 0.252 [0.248, 0.256] | 0.00 | 0.58 | 0.07 | 0.05 | – | 0.00 | 0.00 | – |
| qwen3:4b | named | 120 | 0.254 [0.246, 0.262] | 0.00 | 0.58 | 0.17 | 0.13 | – | 0.00 | 0.00 | – |
| qwen3:14b | named | 80 | 0.271 [0.251, 0.291] | 0.01 | 0.58 | 0.60 | 0.55 | – | 0.00 | 0.01 | – |
| qwen3.5:9b † | abstract | 80 | 0.271 [0.252, 0.292] | 0.04 | 0.57 | 0.57 | 0.31 | – | 0.00 | 0.04 | – |
| qwen3.5:9b † | named | 80 | 0.273 [0.247, 0.297] | 0.05 | 0.59 | 0.89 | 0.36 | – | 0.00 | 0.05 | – |
| random | named | 120 | 0.274 [0.260, 0.288] | 0.00 | 0.57 | 1.50 | 0.38 | – | 0.00 | 0.00 | – |
| gemma3:4b | named | 200 | 0.275 [0.263, 0.286] | 0.00 | 0.57 | 0.51 | 0.39 | – | 0.00 | 0.00 | – |
| qwen3:14b | abstract | 80 | 0.276 [0.263, 0.289] | 0.00 | 0.56 | 0.60 | 0.60 | – | 0.00 | 0.00 | – |
| scripted | named | 120 | 0.276 [0.255, 0.300] | 0.00 | 0.62 | 1.68 | 0.26 | – | 0.00 | 0.00 | – |
| gemma3:4b | abstract | 160 | 0.278 [0.265, 0.291] | 0.01 | 0.57 | 0.51 | 0.42 | – | 0.00 | 0.01 | – |
| llama3.2:3b | named | 200 | 0.280 [0.268, 0.291] | 0.01 | 0.56 | 0.49 | 0.41 | – | 0.00 | 0.01 | – |
| llama3.2:3b | abstract | 320 | 0.291 [0.281, 0.301] | 0.01 | 0.56 | 0.65 | 0.48 | – | 0.00 | 0.01 | – |
| mistral:7b | named | 160 | 0.302 [0.282, 0.324] | 0.00 | 0.56 | 0.71 | 0.28 | – | 0.00 | 0.00 | – |
| mistral:7b | abstract | 160 | 0.303 [0.289, 0.318] | 0.01 | 0.55 | 0.78 | 0.34 | – | 0.00 | 0.01 | – |
| gemma4:e4b † | abstract | 120 | 0.308 [0.284, 0.333] | 0.03 | 0.57 | 1.32 | 0.78 | – | 0.00 | 0.03 | – |
| gemma4:e4b † | named | 120 | 0.322 [0.293, 0.350] | 0.04 | 0.55 | 1.66 | 0.84 | – | 0.00 | 0.04 | – |

## Results: Axiom-Health (exploratory; real NHANES 2017-18 adults, planted exposure)

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| scripted | named | 60 | 0.018 [0.011, 0.027] | 0.88 | 0.98 | 0.02 | 0.02 | – | 0.88 | 0.88 | – |
| random | named | 60 | 0.061 [0.041, 0.083] | 0.55 | 0.91 | 0.18 | 0.25 | – | 0.55 | 0.55 | – |
| gemma4:e4b † | named | 60 | 0.116 [0.092, 0.140] | 0.42 | 0.85 | 0.52 | 0.23 | – | 0.82 | 0.42 | – |
| gemma4:e4b † | abstract | 60 | 0.123 [0.094, 0.152] | 0.42 | 0.85 | 0.75 | 0.20 | – | 0.73 | 0.42 | – |
| qwen3.5:9b † | abstract | 40 | 0.140 [0.104, 0.177] | 0.35 | 0.80 | 0.78 | 0.40 | – | 0.57 | 0.35 | – |
| qwen3.5:9b † | named | 40 | 0.178 [0.144, 0.213] | 0.17 | 0.67 | 0.53 | 0.28 | – | 0.42 | 0.17 | – |
| qwen3:14b | abstract | 20 | 0.206 [0.160, 0.252] | 0.15 | 0.59 | 0.85 | 0.55 | – | 0.40 | 0.15 | – |
| qwen3:14b | named | 20 | 0.217 [0.175, 0.261] | 0.05 | 0.63 | 1.30 | 0.35 | – | 0.30 | 0.05 | – |
| qwen3:4b | named | 60 | 0.238 [0.232, 0.244] | 0.05 | 0.41 | 0.05 | 0.25 | – | 0.48 | 0.05 | – |
| qwen3:4b | abstract | 100 | 0.241 [0.230, 0.250] | 0.07 | 0.43 | 0.14 | 0.29 | – | 0.57 | 0.07 | – |
| gemma3:4b | named | 200 | 0.243 [0.226, 0.260] | 0.07 | 0.50 | 0.49 | 0.34 | – | 0.41 | 0.07 | – |
| llama3.2:3b | abstract | 200 | 0.260 [0.245, 0.274] | 0.04 | 0.47 | 0.59 | 0.35 | – | 0.48 | 0.04 | – |
| mistral:7b | named | 80 | 0.266 [0.247, 0.287] | 0.05 | 0.40 | 0.24 | 0.35 | – | 0.49 | 0.05 | – |
| mistral:7b | abstract | 80 | 0.267 [0.253, 0.281] | 0.03 | 0.37 | 0.23 | 0.31 | – | 0.49 | 0.03 | – |
| gemma3:4b | abstract | 200 | 0.276 [0.258, 0.295] | 0.02 | 0.40 | 0.55 | 0.46 | – | 0.45 | 0.01 | – |
| llama3.2:3b | named | 200 | 0.277 [0.258, 0.295] | 0.03 | 0.44 | 0.68 | 0.41 | – | 0.44 | 0.03 | – |

## Results: Axiom-Ethics (exploratory; real COMPAS risk scores, ProPublica)

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| scripted | named | 60 | 0.014 [0.009, 0.019] | 0.93 | 0.99 | 0.00 | 0.00 | – | 0.93 | 0.93 | – |
| qwen3.5:9b † | abstract | 40 | 0.117 [0.079, 0.158] | 0.50 | 0.85 | 0.40 | 0.20 | – | 0.70 | 0.50 | – |
| random | named | 60 | 0.130 [0.102, 0.160] | 0.40 | 0.84 | 0.60 | 0.32 | – | 0.40 | 0.40 | – |
| gemma4:e4b † | abstract | 58 | 0.145 [0.108, 0.184] | 0.42 | 0.82 | 0.97 | 0.28 | – | 0.67 | 0.43 | – |
| qwen3.5:9b † | named | 40 | 0.156 [0.122, 0.187] | 0.40 | 0.75 | 0.33 | 0.38 | – | 0.72 | 0.40 | – |
| gemma4:e4b † | named | 60 | 0.185 [0.165, 0.206] | 0.10 | 0.73 | 0.67 | 0.37 | – | 0.78 | 0.10 | – |
| qwen3:14b | abstract | 20 | 0.199 [0.169, 0.226] | 0.05 | 0.69 | 0.95 | 0.60 | – | 0.50 | 0.05 | – |
| qwen3:14b | named | 20 | 0.222 [0.184, 0.259] | 0.05 | 0.64 | 1.30 | 0.50 | – | 0.55 | 0.05 | – |
| qwen3:4b | named | 200 | 0.231 [0.217, 0.244] | 0.06 | 0.53 | 0.14 | 0.68 | – | 0.63 | 0.06 | – |
| qwen3:4b | abstract | 80 | 0.242 [0.234, 0.250] | 0.01 | 0.49 | 0.09 | 0.79 | – | 0.55 | 0.01 | – |
| mistral:7b | abstract | 80 | 0.275 [0.256, 0.294] | 0.00 | 0.48 | 0.33 | 0.71 | – | 0.53 | 0.00 | – |
| mistral:7b | named | 80 | 0.277 [0.262, 0.295] | 0.00 | 0.46 | 0.30 | 0.79 | – | 0.53 | 0.00 | – |
| gemma3:4b | abstract | 200 | 0.289 [0.273, 0.303] | 0.01 | 0.50 | 0.82 | 0.68 | – | 0.34 | 0.01 | – |
| llama3.2:3b | abstract | 200 | 0.291 [0.274, 0.309] | 0.00 | 0.49 | 0.82 | 0.74 | – | 0.47 | 0.00 | – |
| gemma3:4b | named | 200 | 0.297 [0.281, 0.315] | 0.00 | 0.50 | 1.00 | 0.72 | – | 0.51 | 0.00 | – |
| llama3.2:3b | named | 200 | 0.303 [0.281, 0.323] | 0.02 | 0.51 | 0.91 | 0.69 | – | 0.31 | 0.01 | – |

† Added after preregistration by model intake or as a hosted model (see `configs/experiment.toml`, `[intake]` and `[hosted]`). Reported, but excluded from the preregistered tests.

## Preregistered hypotheses (see PREREGISTRATION.md)

- **H1** (evaluated): 5/5 models' Brier CI lies wholly above (worse than) the scripted baseline (0.050).
- **H2** (evaluated): llama3.2:3b: trap 0.26 vs mirror denial 0.66, Holm p = 1; qwen3:4b: trap 0.29 vs mirror denial 0.30, Holm p = 1; gemma3:4b: trap 0.28 vs mirror denial 0.41, Holm p = 1; mistral:7b: trap 0.17 vs mirror denial 0.59, Holm p = 1; qwen3:14b: trap 0.28 vs mirror denial 0.15, Holm p = 0.685
- **H3** (evaluated): llama3.2:3b: own claims 0.02 vs ideal analysis of its data 0.66; qwen3:4b: own claims 0.22 vs ideal analysis of its data 0.79; gemma3:4b: own claims 0.12 vs ideal analysis of its data 0.83; mistral:7b: own claims 0.16 vs ideal analysis of its data 0.85; qwen3:14b: own claims 0.69 vs ideal analysis of its data 0.81
- **H4** (evaluated): Spearman rho(size, Brier) = -0.60 (negative = bigger is better; n = 5, p = 0.285)
- **H5** (evaluated): Kendall tau synthetic vs semi-synthetic agent ranking = 1.00 (n = 8)
- **H6** (evaluated): llama3.2:3b: Brier abstract - named = -0.016 (positive = names help); qwen3:4b: Brier abstract - named = +0.008 (positive = names help); gemma3:4b: Brier abstract - named = -0.000 (positive = names help); mistral:7b: Brier abstract - named = +0.019 (positive = names help); qwen3:14b: Brier abstract - named = +0.014 (positive = names help)
- **B1** (evaluated): llama3.2:3b: Brier abstract - named = +0.011 over 40 tasks, Holm p = 0.176; qwen3:4b: Brier abstract - named = -0.002 over 40 tasks, Holm p = 1; gemma3:4b: Brier abstract - named = +0.003 over 40 tasks, Holm p = 1; mistral:7b: Brier abstract - named = +0.001 over 40 tasks, Holm p = 1; qwen3:14b: Brier abstract - named = +0.005 over 40 tasks, Holm p = 1
- **B2** (evaluated): llama3.2:3b: Brier model - reference = +0.015 [-0.011, +0.039]; qwen3:4b: Brier model - reference = -0.025 [-0.048, -0.003]; gemma3:4b: Brier model - reference = +0.001 [-0.023, +0.025]; mistral:7b: Brier model - reference = +0.027 [-0.000, +0.053]; qwen3:14b: Brier model - reference = -0.001 [-0.023, +0.021]
- **B3** (evaluated): llama3.2:3b: claims true 0.17 / reversed 0.15 / indirect 0.17 / confounded 0.15; qwen3:4b: claims true 0.08 / reversed 0.07 / indirect 0.05 / confounded 0.03; gemma3:4b: claims true 0.31 / reversed 0.23 / indirect 0.20 / confounded 0.25; mistral:7b: claims true 0.16 / reversed 0.16 / indirect 0.12 / confounded 0.16; qwen3:14b: claims true 0.30 / reversed 0.14 / indirect 0.23 / confounded 0.29

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
