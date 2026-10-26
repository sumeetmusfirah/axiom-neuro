"""Build results/RESULTS.md and results/summary.json from the ledger.

Everything here is recomputed from scratch on every run, so the report can never drift
from the data. Preregistered hypotheses are evaluated as soon as the data allow.
"""

from __future__ import annotations

import json
from collections import defaultdict


import numpy as np
from scipy import stats

from . import ledger as L
from . import waves as W
from .config import load_config
from .params import REPO
from .planner import make_plan

RESULTS_MD = REPO / "results" / "RESULTS.md"
README = REPO / "README.md"
BOARD_START, BOARD_END = "<!-- leaderboard:start -->", "<!-- leaderboard:end -->"
SUMMARY = REPO / "results" / "summary.json"


def boot_ci(task_means: dict[str, float], n_boot: int = 2000, seed: int = 0):
    """Bootstrap 95% CI resampling tasks (the unit of generalisation)."""
    v = np.array(list(task_means.values()))
    if len(v) == 0:
        return None, None, None
    rng = np.random.default_rng(seed)
    bs = rng.choice(v, (n_boot, len(v))).mean(1)
    return float(v.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def _per_task(rows, fn):
    by = defaultdict(list)
    for r in rows:
        x = fn(r)
        if x is not None:
            by[r["task_id"]].append(float(x))
    return {k: float(np.mean(v)) for k, v in by.items()}


def _cell_name(r):
    return r["agent"] if r["agent"] != "llm" else r["model"]


def summarize(rows: list[dict]) -> dict:
    ok = L.ok_rows(rows)
    cells = defaultdict(list)
    for r in ok:
        cells[(_cell_name(r), r["track"], r["labels"])].append(r)
    out = {}
    for (name, track, lab), rs in sorted(cells.items()):
        m, lo, hi = boot_ci(_per_task(rs, lambda r: r["scores"]["exact"]))
        bm, blo, bhi = boot_ci(_per_task(rs, lambda r: r["scores"]["brier"]))
        trap = [r["scores"]["fell_for_trap"] for r in rs if "fell_for_trap" in r["scores"]]
        handled = [r["confound_handled"] for r in rs if r.get("confound_handled") is not None]
        out[f"{name}|{track}|{lab}"] = {
            "agent": name, "track": track, "labels": lab, "n": len(rs),
            "exact": m, "exact_lo": lo, "exact_hi": hi,
            "edge_acc": float(np.mean([r["scores"]["edge_acc"] for r in rs])),
            "brier": bm, "brier_lo": blo, "brier_hi": bhi,
            "confident_wrong": float(np.mean([r["scores"]["confident_wrong"] for r in rs])),
            "trap_rate": float(np.mean(trap)) if trap else None,
            "confound_handled": float(np.mean(handled)) if handled else None,
            "ideal_on_own_data": float(np.mean([r["ideal_on_own_data"]["exact"] for r in rs])),
            "exact_train": float(np.mean([r["scores"]["exact"] for r in rs if r["split"] == "train"] or [np.nan])),
            "exact_heldout": float(np.mean([r["scores"]["exact"] for r in rs if r["split"] == "heldout"] or [np.nan])),
            "parse_failures": float(np.mean([r.get("parse_failures", 0) for r in rs])),
            "submit_rate": float(np.mean([r.get("submitted", True) for r in rs])),
        }
    return out


MIRROR = {"practice_confound": ("stim_main", "S->Y"), "blink_artifact": ("neural_theta", "L->T")}


def _h2(rows: list[dict], models: list[str]) -> dict:
    """Trap claims on confound tasks vs wrong denials of the same edge on mirror tasks (Fisher, Holm)."""
    ok = [r for r in L.ok_rows(rows) if r["agent"] == "llm" and r["track"] == "synthetic" and r["labels"] == "named"]
    tests = []
    for m in models:
        trap = [r["scores"]["fell_for_trap"] for r in ok if r["model"] == m and r["task_type"] in MIRROR]
        deny = [not r["claims"][edge]["present"] for r in ok if r["model"] == m
                for conf, (mirror, edge) in MIRROR.items() if r["task_type"] == mirror]
        if trap and deny:
            a, b = sum(trap), sum(deny)
            p = stats.fisher_exact([[a, len(trap) - a], [b, len(deny) - b]], alternative="greater").pvalue
            tests.append((m, a / len(trap), b / len(deny), p))
    if not tests:
        return {"id": "H2", "status": "pending"}
    order = sorted(range(len(tests)), key=lambda i: tests[i][3])
    adj, running = [0.0] * len(tests), 0.0
    for rank, i in enumerate(order):  # Holm step-down
        running = max(running, min(1.0, (len(tests) - rank) * tests[i][3]))
        adj[i] = running
    return {"id": "H2", "status": "evaluated",
            "text": "; ".join(f"{m}: trap {t:.2f} vs mirror denial {d:.2f}, Holm p = {adj[i]:.3g}"
                              for i, (m, t, d, _) in enumerate(tests))}


def _bio(rows: list[dict], models: list[str]) -> list[dict]:
    ok = [r for r in L.ok_rows(rows) if r.get("domain") == "bio"]
    out = []
    b1, ps = [], []
    for m in models:
        by = {}
        for r in ok:
            if r["agent"] == "llm" and r["model"] == m:
                by.setdefault((r["task_id"], r["labels"]), []).append(r["scores"]["brier"])
        diffs = [np.mean(by[(t, "abstract")]) - np.mean(by[(t, "named")])
                 for (t, lab) in by if lab == "named" and (t, "abstract") in by]
        if len(diffs) >= 5:
            p = stats.wilcoxon(diffs, alternative="greater").pvalue if any(d != 0 for d in diffs) else 1.0
            b1.append((m, float(np.mean(diffs)), len(diffs)))
            ps.append(p)
    if b1:
        order = sorted(range(len(ps)), key=lambda i: ps[i])
        adj, run = [0.0] * len(ps), 0.0
        for rank, i in enumerate(order):
            run = max(run, min(1.0, (len(ps) - rank) * ps[i]))
            adj[i] = run
        out.append({"id": "B1", "status": "evaluated", "text": "; ".join(
            f"{m}: Brier abstract - named = {d:+.3f} over {n} tasks, Holm p = {adj[i]:.3g}" for i, (m, d, n) in enumerate(b1))})
    else:
        out.append({"id": "B1", "status": "pending"})
    ref = {}
    for r in ok:
        if r["agent"] == "scripted":
            ref.setdefault(r["task_id"], []).append(r["scores"]["brier"])
    b2 = []
    for m in models:
        mine = {}
        for r in ok:
            if r["agent"] == "llm" and r["model"] == m and r["labels"] == "abstract":
                mine.setdefault(r["task_id"], []).append(r["scores"]["brier"])
        common = [t for t in mine if t in ref]
        if len(common) >= 5:
            d = {t: np.mean(mine[t]) - np.mean(ref[t]) for t in common}
            mm, lo, hi = boot_ci(d)
            b2.append(f"{m}: Brier model - reference = {mm:+.3f} [{lo:+.3f}, {hi:+.3f}]")
    out.append({"id": "B2", "status": "evaluated" if b2 else "pending", "text": "; ".join(b2) or None})
    b3 = []
    for m in models:
        rs = [r for r in ok if r["agent"] == "llm" and r["model"] == m and r["labels"] == "named"]
        if rs:
            rate = {}
            for kind in ("true", "reversed", "indirect", "confounded"):
                v = [r["claims"][e]["present"] for r in rs for e, k in r["edge_kinds"].items() if k == kind]
                rate[kind] = np.mean(v) if v else np.nan
            b3.append(f"{m}: claims true {rate['true']:.2f} / reversed {rate['reversed']:.2f} / "
                      f"indirect {rate['indirect']:.2f} / confounded {rate['confounded']:.2f}")
    out.append({"id": "B3", "status": "evaluated" if b3 else "pending", "text": "; ".join(b3) or None})
    return out


def hypotheses(cfg: dict, summ: dict, rows: list[dict] | None = None) -> list[dict]:
    """Automatic, conservative evaluation of PREREGISTRATION.md. 'pending' until data exist."""
    rows = rows or []
    # Preregistered models only; later additions (marked `added`) are reported but not tested here.
    llm_models = [m["name"] for m in cfg["llm"]["models"] if not m.get("added")]
    sizes = {m["name"]: m["params_b"] for m in cfg["llm"]["models"]}
    get = lambda a, t="synthetic", lab="named": summ.get(f"{a}|{t}|{lab}")
    res = []

    scripted = get("scripted")
    h1 = [(m, get(m)) for m in llm_models if get(m)]
    if scripted and h1:
        worse = [m for m, s in h1 if s["brier_lo"] > scripted["brier"]]
        res.append({"id": "H1", "status": "evaluated",
                    "text": f"{len(worse)}/{len(h1)} models' Brier CI lies wholly above (worse than) the scripted "
                            f"baseline ({scripted['brier']:.3f})."})
    else:
        res.append({"id": "H1", "status": "pending"})

    res.append(_h2(rows, llm_models))

    h3 = [(m, get(m)["exact"], get(m)["ideal_on_own_data"]) for m in llm_models if get(m)]
    res.append({"id": "H3", "status": "evaluated" if h3 else "pending",
                "text": "; ".join(f"{m}: own claims {a:.2f} vs ideal analysis of its data {b:.2f}"
                                  for m, a, b in h3) if h3 else None})

    pts = [(sizes[m], get(m)["brier"]) for m in llm_models if get(m)]
    if len(pts) >= 3:
        rho, p = stats.spearmanr([x for x, _ in pts], [y for _, y in pts])
        res.append({"id": "H4", "status": "evaluated", "text": f"Spearman rho(size, Brier) = {rho:.2f} (negative = bigger is better; n = {len(pts)}, p = {p:.3f})"})
    else:
        res.append({"id": "H4", "status": "pending"})

    names = [n for n in ["random", "scripted", "oracle", *llm_models] if get(n) and get(n, "semisynthetic")]
    if len(names) >= 4:
        tau, p = stats.kendalltau([get(n)["brier"] for n in names], [get(n, "semisynthetic")["brier"] for n in names])
        res.append({"id": "H5", "status": "evaluated",
                    "text": f"Kendall tau synthetic vs semi-synthetic agent ranking = {tau:.2f} (n = {len(names)})"})
    else:
        res.append({"id": "H5", "status": "pending"})

    h6 = [(m, get(m, lab="abstract")["brier"] - get(m)["brier"]) for m in llm_models
          if get(m) and get(m, lab="abstract")]
    res.append({"id": "H6", "status": "evaluated" if h6 else "pending",
                "text": "; ".join(f"{m}: Brier abstract - named = {d:+.3f} (positive = names help)" for m, d in h6) if h6 else None})
    return res + _bio(rows, llm_models)


def replication(cfg: dict, rows: list[dict], summ: dict) -> dict:
    """R1 (exploratory): primary-set Brier vs fresh replication waves, synthetic track, named labels."""
    ok = [r for r in L.ok_rows(rows) if r.get("wave") and r["track"] == "synthetic" and r["labels"] == "named"]
    waves = sorted({r["wave"] for r in ok})
    table = []
    for name in sorted({_cell_name(r) for r in ok}):
        prim = summ.get(f"{name}|synthetic|named")
        mine = [r for r in ok if _cell_name(r) == name]
        per_wave = {w: boot_ci(_per_task([r for r in mine if r["wave"] == w], lambda r: r["scores"]["brier"]))[0]
                    for w in waves}
        pooled, lo, hi = boot_ci(_per_task(mine, lambda r: r["scores"]["brier"]))
        table.append({"agent": name, "primary": prim["brier"] if prim else None, "waves": per_wave,
                      "pooled": pooled, "pooled_lo": lo, "pooled_hi": hi})
    both = [t for t in table if t["primary"] is not None and t["pooled"] is not None]
    tau = None
    if len(both) >= 4:
        tau = float(stats.kendalltau([t["primary"] for t in both], [t["pooled"] for t in both])[0])
    return {"waves": waves, "table": table, "kendall_tau": tau, "n_agents": len(both)}


def leaderboard(cfg: dict, summ: dict) -> str:
    added = {m["name"] for m in cfg["llm"]["models"] if m.get("added")}
    sel = sorted((v for v in summ.values() if v["track"] == "synthetic" and v["labels"] == "named"
                  and v["brier"] is not None), key=lambda v: v["brier"])
    if not sel:
        return "_No scored episodes yet._"
    out = ["| # | Agent | Edge Brier [95% CI] (lower is better) | Fell for trap | Episodes |",
           "| --- | --- | --- | --- | --- |"]
    for i, v in enumerate(sel, 1):
        name = v["agent"] + (" †" if v["agent"] in added else "")
        if v["agent"] in ("random", "scripted", "oracle"):
            name = f"*{name} (reference)*"
        out.append(f"| {i} | {name} | {v['brier']:.3f} [{v['brier_lo']:.3f}, {v['brier_hi']:.3f}] "
                   f"| {_f(v['trap_rate'])} | {v['n']} |")
    if added & {v["agent"] for v in sel}:
        out += ["", "† added after preregistration by model intake; not part of the preregistered tests."]
    return "\n".join(out)


def write_leaderboard(board: str, now: str, path=README) -> None:
    if not path.exists():
        return
    text = path.read_text()
    i, j = text.find(BOARD_START), text.find(BOARD_END)
    if i < 0 or j < i:
        return
    body = f"{BOARD_START}\n_Axiom-Neuro, synthetic track, named labels. Data as of {now}._\n\n{board}\n"
    path.write_text(text[:i] + body + text[j:])


def _f(x, nd=2):
    return "–" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{nd}f}"


def build(rows: list[dict] | None = None) -> dict:
    cfg = load_config()
    rows = L.read_rows() if rows is None else rows
    prim = L.primary(rows)
    summ = summarize(prim)
    plan = make_plan(cfg, rows)
    hyp = hypotheses(cfg, summ, prim)
    rep = replication(cfg, rows, summ)
    added = {m["name"] for m in cfg["llm"]["models"] if m.get("added")}
    n_ok = len(L.ok_rows(rows))
    n_err = sum(r["status"] == "error" for r in rows)
    # Stamp the data, not the clock: a run that adds nothing leaves the files byte-identical,
    # so the automation never makes an empty commit.
    now = max((r.get("finished_at", "") for r in rows), default="") or "no data yet"

    md = ["# Axiom-Neuro results", "",
          f"Auto-generated from `results/ledger.jsonl` (data as of {now}). Do not edit by hand.", "",
          f"**Progress:** {n_ok} episodes scored, {n_err} failed attempts logged, "
          f"{plan['n_pending_total']} queued. Setup pending: {', '.join(plan['setup']) or 'none'}.", "",
          "## Gates", "", "| Gate | Passed | Detail |", "| --- | --- | --- |"]
    for k, v in plan["gates"].items():
        detail = {kk: vv for kk, vv in v.items() if kk != "passed"}
        md.append(f"| {k} | {'yes' if v['passed'] else 'no'} | `{json.dumps(detail)}` |")
    titles = {"synthetic": "Axiom-Neuro, synthetic track", "semisynthetic": "Axiom-Neuro, semi-synthetic track (real ERP CORE trials)",
              "sachs": "Axiom-Bio (real single cells, Sachs et al. 2005)"}
    for track in ("synthetic", "semisynthetic", "sachs"):
        sel = {k: v for k, v in summ.items() if v["track"] == track}
        if not sel:
            continue
        md += ["", f"## Results: {titles[track]}", "",
               "| Agent | Labels | n | Brier [95% CI] (primary, lower is better) | Exact match | Edge acc | Confident-wrong / ep | "
               "Fell for trap | Handled confound | Ideal analysis of own data | Train | Held-out |",
               "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for v in sorted(sel.values(), key=lambda v: v["brier"] if v["brier"] is not None else 9):
            md.append(f"| {v['agent']}{' †' if v['agent'] in added else ''} | {v['labels']} | {v['n']} | {_f(v['brier'], 3)} [{_f(v['brier_lo'], 3)}, {_f(v['brier_hi'], 3)}] "
                      f"| {_f(v['exact'])} | {_f(v['edge_acc'])} | {_f(v['confident_wrong'])} | {_f(v['trap_rate'])} "
                      f"| {_f(v['confound_handled'])} | {_f(v['ideal_on_own_data'])} | {_f(v['exact_train'])} | {_f(v['exact_heldout'])} |")
    if added:
        md += ["", "† Added after preregistration by model intake (see `configs/experiment.toml`, `[intake]`). "
               "Reported, but excluded from the preregistered tests."]
    md += ["", "## Preregistered hypotheses (see PREREGISTRATION.md)", ""]
    for h in hyp:
        md.append(f"- **{h['id']}** ({h['status']}): {h.get('text') or 'waiting for data'}")
    md += ["", "## Replication waves (exploratory, R1)", ""]
    if rep["table"]:
        ws = rep["waves"]
        md += ["Fresh task instances from the same hypothesis family, frozen after the primary set finished. "
               "Synthetic track, named labels, edge Brier.", "",
               "| Agent | Primary set | " + " | ".join(f"Wave {w}" for w in ws) + " | All waves [95% CI] |",
               "| --- | --- | " + " | ".join("---" for _ in ws) + " | --- |"]
        for t in sorted(rep["table"], key=lambda t: t["pooled"] if t["pooled"] is not None else 9):
            md.append(f"| {t['agent']} | {_f(t['primary'], 3)} | " + " | ".join(_f(t['waves'][w], 3) for w in ws)
                      + f" | {_f(t['pooled'], 3)} [{_f(t['pooled_lo'], 3)}, {_f(t['pooled_hi'], 3)}] |")
        if rep["kendall_tau"] is not None:
            md += ["", f"Ranking agreement, primary set vs all waves: Kendall tau = {rep['kendall_tau']:.2f} "
                   f"(n = {rep['n_agents']} agents)."]
    else:
        md.append("No wave has run yet. The first wave is frozen once the primary queue is empty.")
    RESULTS_MD.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_MD.write_text("\n".join(md) + "\n")
    write_leaderboard(leaderboard(cfg, summ), now)
    # A data release is due whenever the queue drains: named by the data time, so it is deterministic.
    release = f"results-{now[:10]}" if n_ok and not plan["n_pending_total"] and not plan["setup"] else None
    payload = {"generated": now, "episodes_ok": n_ok, "failed_attempts": n_err,
               "queued": plan["n_pending_total"], "gates": plan["gates"], "cells": summ, "hypotheses": hyp,
               "replication": rep, "release_tag": release,
               "models": [{k: m.get(k) for k in ("name", "params_b", "added", "digest")} for m in cfg["llm"]["models"]],
               "waves": W.index()}
    SUMMARY.write_text(json.dumps(payload, indent=2, default=str))
    return payload
