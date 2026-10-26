# Axiom-Neuro

**Do language models design and analyse experiments like scientists?**
Axiom-Neuro is a simulated cognitive-neuroscience lab with known ground truth, fitted to real human EEG. It tests the part of science that is hardest to grade: experimental judgement.

[![ci](https://github.com/sumeetmusfirah/axiom-neuro/actions/workflows/ci.yml/badge.svg)](https://github.com/sumeetmusfirah/axiom-neuro/actions/workflows/ci.yml)
[![experiments](https://github.com/sumeetmusfirah/axiom-neuro/actions/workflows/experiments.yml/badge.svg)](https://github.com/sumeetmusfirah/axiom-neuro/actions/workflows/experiments.yml)

**[Project page, figures and animations](https://sumeetmusfirah.github.io/axiom-neuro/)** · **[Paper (PDF, rebuilt from live results)](https://sumeetmusfirah.github.io/axiom-neuro/axiom-neuro.pdf)** · **[Open the LaTeX in Overleaf](https://www.overleaf.com/docs?snip_uri=https://sumeetmusfirah.github.io/axiom-neuro/axiom-neuro-overleaf.zip&engine=pdflatex)** · **[Live results](results/RESULTS.md)** · **[Preregistration](PREREGISTRATION.md)** · **[Architecture](docs/ARCHITECTURE.md)**

## Leaderboard

Rebuilt from the ledger after every run. Full tables, both tracks, Axiom-Bio and the hypothesis tests are in [results/RESULTS.md](results/RESULTS.md).

<!-- leaderboard:start -->
_Axiom-Neuro, synthetic track, named labels. Data as of 2026-10-26T00:00:13.171356+00:00._

| # | Agent | Edge Brier [95% CI] (lower is better) | Fell for trap | Episodes |
| --- | --- | --- | --- | --- |
| 1 | *oracle (reference)* | 0.041 [0.036, 0.047] | 0.10 | 180 |
| 2 | *scripted (reference)* | 0.050 [0.043, 0.058] | 0.12 | 180 |
| 3 | *random (reference)* | 0.120 [0.107, 0.134] | 0.08 | 180 |
<!-- leaderboard:end -->

## The idea in one paragraph

An AI scientist is dropped into a lab studying cognitive control. Participants do a flanker task under different working-memory loads, with real or sham brain stimulation (tES) and EEG. Somewhere in the lab is a hidden causal mechanism: does load slow people down? Does stimulation help, only under high load, or not at all? Is that frontal-theta effect neural, or just blinks? The agent gets a pilot study (sometimes deliberately confounded), a budget of 30 participant-hours, and standard analysis tools. It must design experiments, analyse them, and submit a calibrated claim for every causal edge. Scoring is arithmetic against the hidden truth, with **no LLM judge anywhere**.

## Axiom-Bio: the same question on real cells

A second lab runs on real single-cell data: 7,466 human T cells from Sachs et al. (2005), 11 signalling molecules, nine real drug conditions. The agent buys cells and must say which molecules *directly* regulate which. Candidates mix true arrows with reversed, indirect and shared-regulator traps. Real pharmacology adds two more: a MEK inhibitor *raises* measured Mek, and two conditions lack the standard stimulation. Because most of the network can't be identified from these interventions alone, running each model with real names and again with abstract labels (M1–M11) separates **recalling textbook biology** from **reading the data**.

## Why it is built this way

My [previous study](https://github.com/Project-Aletheia-org/aletheia-pressure-evals) found that two LLM judges scoring the same 180 outputs agreed at chance, and one gave its own model family zero on everything. Evaluations that grade prose inherit that unreliability. A world where the answer is known removes it.

## Contributions

1. **Judge-free evaluation of scientific judgement at the human-experiment level.** Existing neuroscience discovery benchmarks work at the circuit level (a digital fly, an in-silico zebrafish, single neurons). Axiom-Neuro targets population-level causal claims from noisy humans, where counterbalancing, factorial design and artifact handling decide the answer.
2. **Planted traps with mirror controls.** A stimulation "effect" that is really practice (the active block always came second), and a theta "effect" that is really blinks. Each trap has a held-out mirror task with the same pilot data and the opposite truth, so blanket scepticism doesn't score.
3. **Grounded in real data, twice.** Noise, individual differences and artifacts are fitted to the [ERP CORE](https://erpinfo.org/erp-core) flanker dataset (40 participants) and validated by 5-fold cross-validation, so each of the 40 participants is held out once. A second, semi-synthetic track runs every experiment on *real* ERP CORE trials with known effects injected on top. Whether the two tracks agree is a preregistered test.
4. **A design-versus-analysis decomposition.** An ideal analyst re-analyses each agent's own data. This splits every failure into "ran the wrong experiment" and "misread the right one", which is the most actionable thing to know about an AI scientist.
5. **Recall versus inference on real biology.** Axiom-Bio runs the same agents on real single cells, where comparing named and abstract labels measures how much a model knows versus how much it can infer.
6. **A preregistered study that runs itself, for $0.** Hypotheses, metric and stopping rule were fixed before any model ran. Gates in code block model runs until the fit validates, reference agents order correctly and tasks are frozen. GitHub Actions runs local open-weight models every 6 hours, commits only real results, rebuilds the figures, animations and paper, and opens an issue if anything stalls.
7. **It doesn't stop at the frozen set.** When the queue drains, the engine freezes a fresh *replication wave* of unseen tasks (seeds fixed in advance) to test whether rankings hold on new instances. A weekly intake adds the next open model, pinned to its registry digest. Each time the queue empties it cuts a versioned data release.

## What an episode looks like

![episode](https://sumeetmusfirah.github.io/axiom-neuro/animations/demo_reference.gif)

*The scripted reference agent on the practice trap. Blue bars: what the data collected so far actually support, according to the ideal analyst. Black ticks: the truth. Orange diamonds, at the end: what the agent claimed. Language-model replays are on the [project page](https://sumeetmusfirah.github.io/axiom-neuro/) once results land.*

## How the traps work

![traps](https://sumeetmusfirah.github.io/axiom-neuro/figures/fig_trap_mechanics.png)

*Computed from the simulator. Grey: the effect the pilot suggests. Blue: what a careful experiment recovers. The effect vanishes on each trap task and survives on its held-out mirror.*

## The paper

The LaTeX source is in [`paper/`](paper/): `main.tex`, `refs.bib`, and tables and figures generated from the results ledger. Every push rebuilds the PDF, an arXiv tarball and an Overleaf zip. [Open in Overleaf](https://www.overleaf.com/docs?snip_uri=https://sumeetmusfirah.github.io/axiom-neuro/axiom-neuro-overleaf.zip&engine=pdflatex) imports the current version as a new project, figures included.

## Quick start

```bash
uv venv --python 3.11 && uv pip install -e ".[dev,viz]"
axiom smoke                      # baselines on one task of each type, ~10 s
pytest -q

# Full pipeline, exactly as the automation runs it:
uv pip install -e ".[fit]" && axiom fit-erpcore   # download + fit ERP CORE (~30 min)
axiom oracle && axiom freeze
axiom plan && axiom run --shard 0 --out results/incoming/local.jsonl
axiom collect && axiom report && axiom figures && axiom paper-tables
```

LLM runs need [Ollama](https://ollama.com) with the models in `configs/experiment.toml`.

## Layout

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). In short: `configs/experiment.toml` decides what runs. `src/axiom_neuro/` holds the lab, the agents and the scoring. `.github/workflows/` keeps it running. `results/` is the public ledger.

## Data and licence

Code: MIT. Derived ERP CORE data in `data/`: CC BY-SA 4.0, from Kappenman et al. (2021), *NeuroImage* 225:117465. Sachs single-cell data: CC BY 4.0 via Zenodo 7681811, from Sachs et al. (2005), *Science* 308:523. See [data/README.md](data/README.md).

## Citation

```bibtex
@misc{musfirah2026axiomneuro,
  title  = {Axiom-Neuro: Do Language Models Design and Analyse Experiments Like Scientists?},
  author = {Musfirah, Sumeet},
  year   = {2026},
  url    = {https://github.com/sumeetmusfirah/axiom-neuro}
}
```
