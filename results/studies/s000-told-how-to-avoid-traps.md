# Study s000-told-how-to-avoid-traps

**Question.** If a model is told exactly how to avoid the two traps, does it stop falling for them?

**Hypothesis (registered before any episode ran).** Trap rates drop but do not reach the scripted baseline: knowing the rule is not the same as applying it inside a multi-step episode.

**Change from the main study.** `instruction = 'Two pitfalls matter here. (1) If stimulation was always given in the second block, practice can masquerade as a stimulation effect: run a design with counterbalanced or between-subjects order before claiming S->Y. (2) Blinks inflate frontal theta: enable ICA or run an artifact check before claiming L->T.'`

**Progress.** 165 of 200 episodes — still running.

Brier is the mean edge Brier score (lower is better). Difference = study minus the main study's episodes for the same model, track, labels and tasks; 95% CI by bootstrap over tasks.

| Model | Track | Labels | n | Study Brier | Main-study Brier | Difference [95% CI] | Verdict | Fell for trap | Analysis error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| llama3.2:3b | synthetic | named | 40 | 0.276 | 0.287 | -0.011 [-0.048, 0.022] | no clear difference | 0.25 | 0.190 |
| qwen3:4b | synthetic | named | 40 | 0.146 | 0.160 | -0.004 [-0.054, 0.048] | no clear difference | 0.20 | 0.081 |
| gemma3:4b | synthetic | named | 40 | 0.241 | 0.257 | -0.011 [-0.053, 0.028] | no clear difference | 0.30 | 0.169 |
| mistral:7b | synthetic | named | 31 | 0.255 | – | – (no paired baseline yet) | – | 0.15 | 0.183 |
| qwen3:14b | synthetic | named | 14 | 0.127 | – | – (no paired baseline yet) | – | 0.30 | 0.078 |

Exploratory: decided after the preregistration and kept out of every preregistered test.
