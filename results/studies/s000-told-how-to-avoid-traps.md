# Study s000-told-how-to-avoid-traps

**Question.** If a model is told exactly how to avoid the two traps, does it stop falling for them?

**Hypothesis (registered before any episode ran).** Trap rates drop but do not reach the scripted baseline: knowing the rule is not the same as applying it inside a multi-step episode.

**Change from the main study.** `instruction = 'Two pitfalls matter here. (1) If stimulation was always given in the second block, practice can masquerade as a stimulation effect: run a design with counterbalanced or between-subjects order before claiming S->Y. (2) Blinks inflate frontal theta: enable ICA or run an artifact check before claiming L->T.'`

**Progress.** 0 of 200 episodes — still running.

Brier is the mean edge Brier score (lower is better). Difference = study minus the main study's episodes for the same model, track, labels and tasks; 95% CI by bootstrap over tasks.

| Model | Track | Labels | n | Study Brier | Main-study Brier | Difference [95% CI] | Verdict | Fell for trap | Analysis error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| llama3.2:3b | synthetic | named | 0 | – | – | – (no paired baseline yet) | – | – | – |
| qwen3:4b | synthetic | named | 0 | – | – | – (no paired baseline yet) | – | – | – |
| gemma3:4b | synthetic | named | 0 | – | – | – (no paired baseline yet) | – | – | – |
| mistral:7b | synthetic | named | 0 | – | – | – (no paired baseline yet) | – | – | – |
| qwen3:14b | synthetic | named | 0 | – | – | – (no paired baseline yet) | – | – | – |

Exploratory: decided after the preregistration and kept out of every preregistered test.
