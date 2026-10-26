# Studies

Experiments decided after the preregistration. One TOML file per study; committing the file
registers it, and the engine runs it ahead of the main queue on the next cycle.

The easy way is the **New experiment** issue form: it writes the file, starts the engine and posts
the result back to the issue. To write one by hand:

```toml
id = "s010-more-turns"            # file name without .toml
question = "Do models do better with twice the turns?"
hypothesis = "Brier improves for the 7B+ models only."
models = "all"                    # or ["qwen3:4b", "mistral:7b"]; any Ollama tag works
tracks = ["synthetic"]            # synthetic | semisynthetic | sachs
labels = ["named"]                # named | abstract
task_types = []                   # [] = all; or e.g. ["practice_confound", "stim_main"]
seeds = 1

[change]                          # anything omitted stays as in configs/experiment.toml
max_turns = 24
# temperature = 0.0
# budget_participant_hours = 60   # neuro only
# instruction = "Always counterbalance block order."
```

Each study is scored exactly like the main study and compared with the main study's episodes for
the same model, track, labels and tasks (paired by task, bootstrap CI). Reports land in
`results/studies/<id>.md`. Study rows never enter the preregistered analysis.
