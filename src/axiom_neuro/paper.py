"""Write paper/generated/*.tex from the ledger, so every number in the PDF is computed.

With no data, the generated text says so plainly. Nothing is ever filled in by hand.
"""

from __future__ import annotations

import json

from . import ledger as L
from .config import load_config
from .params import FITTED_PATH, REPO
from .report import summarize

GEN = REPO / "paper" / "generated"


def _f(x, nd=3):
    return "--" if x is None or x != x else f"{x:.{nd}f}"


def build() -> list[str]:
    GEN.mkdir(parents=True, exist_ok=True)
    cfg = load_config()
    rows = L.read_rows()
    ok = L.ok_rows(rows)
    summ = summarize(rows)
    llm_n = sum(r["agent"] == "llm" for r in ok)

    fit = json.loads(FITTED_PATH.read_text()) if FITTED_PATH.exists() else None
    if fit:
        v = fit["validation"]
        status = (f"The fitted simulator {'passed' if v['passed'] else 'did not pass'} the held-out check "
                  f"({v['n_heldout']} held-out participants vs {v['n_sim_participants']} simulated; "
                  f"criterion: {v['criteria']}).")
    else:
        status = "The ERP CORE fit has not run yet."
    macros = [
        f"\\newcommand{{\\nEpisodes}}{{{len(ok)}}}",
        f"\\newcommand{{\\nLLMEpisodes}}{{{llm_n}}}",
        f"\\newcommand{{\\nModels}}{{{len(cfg['llm']['models'])}}}",
        f"\\newcommand{{\\fitStatus}}{{{status}}}",
        f"\\newcommand{{\\resultsStatus}}{{"
        + ("No language-model episodes have completed yet; this section fills in automatically as the "
           "experiment engine runs. Baseline results are reported below."
           if llm_n == 0 else f"Results below cover {llm_n} language-model episodes and {len(ok) - llm_n} "
                              "baseline episodes, regenerated from the public ledger on every build.") + "}",
    ]
    (GEN / "macros.tex").write_text("\n".join(macros) + "\n")

    lines = [r"\begin{tabular}{llrrrrr}", r"\toprule",
             r"Agent & Track & $n$ & Brier $\downarrow$ & Exact & Trap & Ideal-on-own \\", r"\midrule"]
    order = ["random", "scripted", "oracle", *[m["name"] for m in cfg["llm"]["models"]]]
    body = []
    for name in order:
        for track in ("synthetic", "semisynthetic"):
            c = summ.get(f"{name}|{track}|named")
            if c:
                tex_name = name.replace("_", "\\_")
                body.append(f"{tex_name} & {track} & {c['n']} & {_f(c['brier'])} & {_f(c['exact'], 2)} "
                            f"& {_f(c['trap_rate'], 2)} & {_f(c['ideal_on_own_data'], 2)} \\\\")
    lines += body or [r"\multicolumn{7}{c}{\emph{No completed episodes yet.}} \\"]
    lines += [r"\bottomrule", r"\end{tabular}"]
    (GEN / "results_table.tex").write_text("\n".join(lines) + "\n")
    return [str(p.relative_to(REPO)) for p in sorted(GEN.glob("*.tex"))]
