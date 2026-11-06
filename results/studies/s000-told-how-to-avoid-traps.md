# Study s000-told-how-to-avoid-traps

**Question.** If a model is told exactly how to avoid the two traps, does it stop falling for them?

**Hypothesis (registered before any episode ran).** Trap rates drop but do not reach the scripted baseline: knowing the rule is not the same as applying it inside a multi-step episode.

**Change from the main study.** `instruction = 'Two pitfalls matter here. (1) If stimulation was always given in the second block, practice can masquerade as a stimulation effect: run a design with counterbalanced or between-subjects order before claiming S->Y. (2) Blinks inflate frontal theta: enable ICA or run an artifact check before claiming L->T.'`

**Progress.** 285 of 500 episodes — still running.

Brier is the mean edge Brier score (lower is better). Difference = study minus the main study's episodes for the same model, track, labels and tasks; 95% CI by bootstrap over tasks.

| Model | Track | Labels | n | Study Brier | Main-study Brier | Difference [95% CI] | Verdict | Fell for trap | Analysis error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| llama3.2:3b | synthetic | named | 40 | 0.276 | 0.301 | -0.025 [-0.053, 0.003] | no clear difference | 0.25 | 0.190 |
| qwen3:4b | synthetic | named | 40 | 0.146 | 0.170 | -0.024 [-0.062, 0.015] | no clear difference | 0.20 | 0.081 |
| gemma3:4b | synthetic | named | 40 | 0.241 | 0.233 | 0.008 [-0.018, 0.035] | no clear difference | 0.30 | 0.169 |
| mistral:7b | synthetic | named | 40 | 0.258 | 0.240 | 0.018 [-0.024, 0.059] | no clear difference | 0.15 | 0.176 |
| qwen3:14b | synthetic | named | 40 | 0.120 | 0.126 | -0.005 [-0.021, 0.011] | no clear difference | 0.20 | 0.054 |
| gemma4:12b | synthetic | named | 5 | 0.096 | – | – (no paired baseline yet) | – | 1.00 | 0.019 |
| qwen3.5:9b | synthetic | named | 40 | 0.116 | – | – (no paired baseline yet) | – | 0.05 | 0.072 |
| gemma4:e4b | synthetic | named | 40 | 0.088 | 0.101 | -0.008 [-0.038, 0.024] | no clear difference | 0.30 | 0.036 |

Exploratory: decided after the preregistration and kept out of every preregistered test.
