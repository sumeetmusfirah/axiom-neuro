# Axiom-Neuro results

Auto-generated from `results/ledger.jsonl` (data as of 2026-11-04T07:38:52.039723+00:00). Do not edit by hand.

**Progress:** 3353 episodes scored, 12 failed attempts logged, 1387 queued. Setup pending: none.

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
| qwen3:14b | named | 30 | 0.131 [0.117, 0.145] | 0.80 | 0.97 | 0.17 | 0.40 | 1.00 | 0.73 | 0.80 | – |
| qwen3:4b | named | 120 | 0.165 [0.147, 0.181] | 0.28 | 0.80 | 0.42 | 0.25 | 0.79 | 0.79 | 0.26 | 0.30 |
| qwen3:4b | abstract | 108 | 0.199 [0.179, 0.218] | 0.10 | 0.75 | 0.94 | 0.16 | 0.74 | 0.82 | 0.08 | 0.10 |
| gemma3:4b | abstract | 120 | 0.231 [0.213, 0.249] | 0.11 | 0.72 | 0.71 | 0.38 | 0.90 | 0.88 | 0.03 | 0.28 |
| gemma3:4b | named | 120 | 0.245 [0.230, 0.261] | 0.11 | 0.71 | 0.57 | 0.28 | 0.94 | 0.88 | 0.09 | 0.15 |
| mistral:7b | named | 60 | 0.261 [0.228, 0.295] | 0.13 | 0.74 | 0.53 | 0.10 | 0.80 | 0.85 | 0.12 | 0.15 |
| mistral:7b | abstract | 54 | 0.276 [0.248, 0.306] | 0.02 | 0.70 | 0.91 | 0.20 | 0.88 | 0.85 | 0.00 | 0.07 |
| llama3.2:3b | abstract | 136 | 0.288 [0.272, 0.305] | 0.03 | 0.62 | 0.65 | 0.12 | 0.78 | 0.62 | 0.04 | 0.00 |
| llama3.2:3b | named | 180 | 0.298 [0.284, 0.313] | 0.03 | 0.60 | 0.83 | 0.35 | 0.71 | 0.64 | 0.04 | 0.02 |

## Results: Axiom-Neuro, semi-synthetic track (real ERP CORE trials)

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| oracle | named | 180 | 0.044 [0.039, 0.049] | 0.77 | 0.96 | 0.03 | 0.18 | 1.00 | 0.77 | 0.75 | 0.80 |
| scripted | named | 180 | 0.049 [0.044, 0.053] | 0.76 | 0.96 | 0.03 | 0.15 | 1.00 | 0.76 | 0.77 | 0.73 |
| random | named | 180 | 0.098 [0.086, 0.111] | 0.57 | 0.91 | 0.14 | 0.08 | 0.69 | 0.57 | 0.54 | 0.62 |
| qwen3:4b | named | 60 | 0.159 [0.134, 0.186] | 0.30 | 0.80 | 0.53 | 0.20 | 0.78 | 0.90 | 0.25 | 0.40 |
| qwen3:4b | abstract | 60 | 0.176 [0.152, 0.197] | 0.15 | 0.78 | 0.73 | 0.00 | 0.82 | 0.90 | 0.15 | 0.15 |
| gemma3:4b | named | 75 | 0.231 [0.210, 0.252] | 0.12 | 0.72 | 0.52 | 0.20 | 0.92 | 0.92 | 0.09 | 0.10 |
| gemma3:4b | abstract | 60 | 0.250 [0.227, 0.276] | 0.10 | 0.69 | 0.78 | 0.50 | 0.97 | 0.95 | 0.05 | 0.20 |
| llama3.2:3b | abstract | 120 | 0.279 [0.266, 0.295] | 0.03 | 0.64 | 0.61 | 0.28 | 0.82 | 0.68 | 0.03 | 0.03 |
| llama3.2:3b | named | 120 | 0.304 [0.288, 0.321] | 0.03 | 0.57 | 0.87 | 0.40 | 0.84 | 0.73 | 0.05 | 0.00 |

## Results: Axiom-Bio (real single cells, Sachs et al. 2005)

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen3:4b | abstract | 40 | 0.255 [0.251, 0.261] | 0.00 | 0.58 | 0.15 | 0.10 | – | 0.00 | 0.00 | – |
| qwen3:4b | named | 40 | 0.257 [0.242, 0.273] | 0.00 | 0.57 | 0.20 | 0.17 | – | 0.00 | 0.00 | – |
| llama3.2:3b | named | 80 | 0.271 [0.256, 0.289] | 0.01 | 0.58 | 0.40 | 0.36 | – | 0.00 | 0.01 | – |
| gemma3:4b | named | 40 | 0.272 [0.252, 0.293] | 0.00 | 0.57 | 0.35 | 0.35 | – | 0.00 | 0.00 | – |
| random | named | 120 | 0.274 [0.260, 0.288] | 0.00 | 0.57 | 1.50 | 0.38 | – | 0.00 | 0.00 | – |
| scripted | named | 120 | 0.276 [0.255, 0.300] | 0.00 | 0.62 | 1.68 | 0.26 | – | 0.00 | 0.00 | – |
| qwen3:14b | abstract | 28 | 0.279 [0.260, 0.300] | 0.00 | 0.55 | 0.57 | 0.64 | – | 0.00 | 0.00 | – |
| llama3.2:3b | abstract | 80 | 0.283 [0.263, 0.306] | 0.01 | 0.58 | 0.56 | 0.39 | – | 0.00 | 0.01 | – |
| gemma3:4b | abstract | 40 | 0.296 [0.275, 0.319] | 0.00 | 0.53 | 0.82 | 0.45 | – | 0.00 | 0.00 | – |
| mistral:7b | named | 22 | 0.298 [0.258, 0.348] | 0.00 | 0.58 | 0.73 | 0.41 | – | 0.00 | 0.00 | – |
| mistral:7b | abstract | 40 | 0.308 [0.277, 0.345] | 0.00 | 0.55 | 0.78 | 0.33 | – | 0.00 | 0.00 | – |

## Preregistered hypotheses (see PREREGISTRATION.md)

- **H1** (evaluated): 5/5 models' Brier CI lies wholly above (worse than) the scripted baseline (0.050).
- **H2** (evaluated): llama3.2:3b: trap 0.35 vs mirror denial 0.58, Holm p = 1; qwen3:4b: trap 0.25 vs mirror denial 0.30, Holm p = 1; gemma3:4b: trap 0.28 vs mirror denial 0.38, Holm p = 1; mistral:7b: trap 0.10 vs mirror denial 0.50, Holm p = 1
- **H3** (evaluated): llama3.2:3b: own claims 0.03 vs ideal analysis of its data 0.64; qwen3:4b: own claims 0.28 vs ideal analysis of its data 0.79; gemma3:4b: own claims 0.11 vs ideal analysis of its data 0.88; mistral:7b: own claims 0.13 vs ideal analysis of its data 0.85; qwen3:14b: own claims 0.80 vs ideal analysis of its data 0.73
- **H4** (evaluated): Spearman rho(size, Brier) = -0.60 (negative = bigger is better; n = 5, p = 0.285)
- **H5** (evaluated): Kendall tau synthetic vs semi-synthetic agent ranking = 1.00 (n = 6)
- **H6** (evaluated): llama3.2:3b: Brier abstract - named = -0.010 (positive = names help); qwen3:4b: Brier abstract - named = +0.034 (positive = names help); gemma3:4b: Brier abstract - named = -0.014 (positive = names help); mistral:7b: Brier abstract - named = +0.015 (positive = names help)
- **B1** (evaluated): llama3.2:3b: Brier abstract - named = +0.012 over 40 tasks, Holm p = 0.525; qwen3:4b: Brier abstract - named = -0.001 over 40 tasks, Holm p = 0.811; gemma3:4b: Brier abstract - named = +0.024 over 40 tasks, Holm p = 0.213; mistral:7b: Brier abstract - named = +0.019 over 22 tasks, Holm p = 0.811
- **B2** (evaluated): llama3.2:3b: Brier model - reference = +0.007 [-0.026, +0.039]; qwen3:4b: Brier model - reference = -0.021 [-0.045, +0.002]; gemma3:4b: Brier model - reference = +0.020 [-0.010, +0.048]; mistral:7b: Brier model - reference = +0.032 [-0.007, +0.073]; qwen3:14b: Brier model - reference = -0.001 [-0.034, +0.030]
- **B3** (evaluated): llama3.2:3b: claims true 0.20 / reversed 0.11 / indirect 0.16 / confounded 0.12; qwen3:4b: claims true 0.09 / reversed 0.11 / indirect 0.02 / confounded 0.06; gemma3:4b: claims true 0.31 / reversed 0.22 / indirect 0.20 / confounded 0.29; mistral:7b: claims true 0.24 / reversed 0.27 / indirect 0.17 / confounded 0.11

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
