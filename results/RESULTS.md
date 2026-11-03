# Axiom-Neuro results

Auto-generated from `results/ledger.jsonl` (data as of 2026-11-03T13:13:00.214377+00:00). Do not edit by hand.

**Progress:** 2652 episodes scored, 12 failed attempts logged, 1348 queued. Setup pending: none.

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
| qwen3:14b | named | 2 | 0.141 [0.103, 0.179] | 0.50 | 0.92 | 0.50 | 0.50 | 1.00 | 0.50 | 0.50 | – |
| qwen3:4b | named | 60 | 0.150 [0.124, 0.176] | 0.33 | 0.84 | 0.38 | 0.30 | 0.88 | 0.80 | 0.33 | 0.35 |
| qwen3:4b | abstract | 35 | 0.208 [0.179, 0.237] | 0.06 | 0.74 | 1.06 | 0.10 | 0.73 | 0.74 | 0.07 | 0.00 |
| gemma3:4b | named | 60 | 0.239 [0.217, 0.264] | 0.15 | 0.73 | 0.52 | 0.35 | 0.90 | 0.87 | 0.12 | 0.20 |
| gemma3:4b | abstract | 35 | 0.240 [0.204, 0.277] | 0.11 | 0.71 | 0.83 | 0.40 | 0.80 | 0.80 | 0.07 | 0.40 |
| mistral:7b | named | 53 | 0.265 [0.230, 0.304] | 0.11 | 0.72 | 0.55 | 0.10 | 0.76 | 0.87 | 0.12 | 0.08 |
| llama3.2:3b | abstract | 120 | 0.288 [0.271, 0.305] | 0.03 | 0.62 | 0.67 | 0.12 | 0.79 | 0.62 | 0.05 | 0.00 |
| llama3.2:3b | named | 120 | 0.295 [0.279, 0.310] | 0.03 | 0.61 | 0.80 | 0.33 | 0.72 | 0.63 | 0.04 | 0.03 |

## Results: Axiom-Neuro, semi-synthetic track (real ERP CORE trials)

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| oracle | named | 180 | 0.044 [0.039, 0.049] | 0.77 | 0.96 | 0.03 | 0.18 | 1.00 | 0.77 | 0.75 | 0.80 |
| scripted | named | 180 | 0.049 [0.044, 0.053] | 0.76 | 0.96 | 0.03 | 0.15 | 1.00 | 0.76 | 0.77 | 0.73 |
| random | named | 180 | 0.098 [0.086, 0.111] | 0.57 | 0.91 | 0.14 | 0.08 | 0.69 | 0.57 | 0.54 | 0.62 |
| qwen3:4b | named | 13 | 0.161 [0.101, 0.224] | 0.31 | 0.79 | 0.62 | 0.20 | 0.80 | 0.85 | 0.31 | – |
| qwen3:4b | abstract | 60 | 0.176 [0.152, 0.197] | 0.15 | 0.78 | 0.73 | 0.00 | 0.82 | 0.90 | 0.15 | 0.15 |
| gemma3:4b | named | 40 | 0.243 [0.215, 0.269] | 0.10 | 0.70 | 0.57 | 0.20 | 0.90 | 0.90 | 0.13 | 0.00 |
| gemma3:4b | abstract | 60 | 0.250 [0.227, 0.276] | 0.10 | 0.69 | 0.78 | 0.50 | 0.97 | 0.95 | 0.05 | 0.20 |
| llama3.2:3b | abstract | 60 | 0.288 [0.269, 0.308] | 0.02 | 0.64 | 0.68 | 0.40 | 0.78 | 0.72 | 0.00 | 0.05 |
| llama3.2:3b | named | 84 | 0.318 [0.298, 0.340] | 0.03 | 0.55 | 1.01 | 0.40 | 0.80 | 0.71 | 0.05 | 0.00 |

## Results: Axiom-Bio (real single cells, Sachs et al. 2005)

| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen3:4b | abstract | 40 | 0.255 [0.251, 0.261] | 0.00 | 0.58 | 0.15 | 0.10 | – | 0.00 | 0.00 | – |
| qwen3:4b | named | 40 | 0.257 [0.242, 0.273] | 0.00 | 0.57 | 0.20 | 0.17 | – | 0.00 | 0.00 | – |
| llama3.2:3b | named | 40 | 0.266 [0.251, 0.283] | 0.03 | 0.60 | 0.42 | 0.38 | – | 0.00 | 0.03 | – |
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
- **H2** (evaluated): llama3.2:3b: trap 0.33 vs mirror denial 0.57, Holm p = 1; qwen3:4b: trap 0.30 vs mirror denial 0.15, Holm p = 0.901; gemma3:4b: trap 0.35 vs mirror denial 0.30, Holm p = 1; mistral:7b: trap 0.10 vs mirror denial 0.69, Holm p = 1
- **H3** (evaluated): llama3.2:3b: own claims 0.03 vs ideal analysis of its data 0.63; qwen3:4b: own claims 0.33 vs ideal analysis of its data 0.80; gemma3:4b: own claims 0.15 vs ideal analysis of its data 0.87; mistral:7b: own claims 0.11 vs ideal analysis of its data 0.87; qwen3:14b: own claims 0.50 vs ideal analysis of its data 0.50
- **H4** (evaluated): Spearman rho(size, Brier) = -0.60 (negative = bigger is better; n = 5, p = 0.285)
- **H5** (evaluated): Kendall tau synthetic vs semi-synthetic agent ranking = 1.00 (n = 6)
- **H6** (evaluated): llama3.2:3b: Brier abstract - named = -0.007 (positive = names help); qwen3:4b: Brier abstract - named = +0.057 (positive = names help); gemma3:4b: Brier abstract - named = +0.001 (positive = names help)
- **B1** (evaluated): llama3.2:3b: Brier abstract - named = +0.014 over 40 tasks, Holm p = 0.488; qwen3:4b: Brier abstract - named = -0.001 over 40 tasks, Holm p = 0.811; gemma3:4b: Brier abstract - named = +0.024 over 40 tasks, Holm p = 0.213; mistral:7b: Brier abstract - named = +0.019 over 22 tasks, Holm p = 0.811
- **B2** (evaluated): llama3.2:3b: Brier model - reference = +0.004 [-0.027, +0.034]; qwen3:4b: Brier model - reference = -0.021 [-0.045, +0.002]; gemma3:4b: Brier model - reference = +0.020 [-0.010, +0.048]; mistral:7b: Brier model - reference = +0.032 [-0.007, +0.073]; qwen3:14b: Brier model - reference = -0.001 [-0.034, +0.030]
- **B3** (evaluated): llama3.2:3b: claims true 0.23 / reversed 0.11 / indirect 0.16 / confounded 0.12; qwen3:4b: claims true 0.09 / reversed 0.11 / indirect 0.02 / confounded 0.06; gemma3:4b: claims true 0.31 / reversed 0.22 / indirect 0.20 / confounded 0.29; mistral:7b: claims true 0.24 / reversed 0.27 / indirect 0.17 / confounded 0.11

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
