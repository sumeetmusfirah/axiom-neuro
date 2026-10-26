# Data

`erpcore_trials.csv.gz` and `fitted_params.json` are derived from **ERP CORE** (ERN flanker task):

> Kappenman, E. S., Farrens, J. L., Zhang, W., Stewart, A. X., & Luck, S. J. (2021).
> ERP CORE: An open resource for human event-related potential research. *NeuroImage*, 225, 117465.
> Data: https://doi.org/10.18115/D5JW4R

ERP CORE is shared under **CC BY-SA 4.0**, and these derived files are shared under the same license
(see `LICENSE` in this folder). Each row is one trial: congruency, RT, correctness, frontal theta
(log 4–8 Hz power at FCz, 0–600 ms) and a blink flag: a large vertical-EOG deflection (peak-to-peak > 100 µV, −200 to 800 ms), which captures blinks and vertical eye movements, both of which contaminate frontal EEG.
Regenerate with `axiom fit-erpcore`.

## Sachs et al. (2005) single-cell signalling data

`sachs_cells.csv.gz` (7,466 cells, 9 conditions) and `sachs_ground_truth.json` (20-edge consensus graph) come from
Zenodo record [7681811](https://zenodo.org/records/7681811) (CC BY 4.0), which redistributes:

> Sachs, K., Perez, O., Pe'er, D., Lauffenburger, D. A., & Nolan, G. P. (2005). Causal protein-signaling networks
> derived from multiparameter single-cell data. *Science*, 308(5721), 523–529.

Five ICAM-2 + inhibitor files in that record, which its own description labels "simulated", are excluded.
Reagent targets follow Sachs et al. and standard pharmacology; the record's own target column is misaligned.
Regenerate with `axiom bio-setup`.
