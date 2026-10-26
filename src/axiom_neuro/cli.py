"""axiom <command>. Every command the automation runs is runnable by hand, identically."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from . import ledger as L
from .config import load_config
from .params import load_params


def cmd_fit(a):
    from .erpcore.fit import run
    out = run(a.participants)
    v = out["validation"]
    print(json.dumps({"validation_passed": v["passed"], "checks": v["checks"]}, indent=2))
    return 0 if v["passed"] else 2


def cmd_oracle(a):
    from .agents.baselines import precompute_oracle
    cfg = load_config()
    res = precompute_oracle(load_params(), cfg["tasks"]["budget_participant_hours"], a.sims)
    print(json.dumps(res, indent=2))
    return 0


def cmd_bio_setup(a):
    from .bio.data import fetch
    from .bio.lab import BIO_MANIFEST, build_bio_tasks, freeze_bio
    print(json.dumps(fetch()))
    cfg = load_config()["bio"]
    if BIO_MANIFEST.exists() and not a.force:
        print(f"bio tasks already frozen: {BIO_MANIFEST}")
    else:
        print("bio tasks frozen sha256=" + freeze_bio(build_bio_tasks(cfg["seed"], cfg["n_tasks"])))
    return 0


def cmd_freeze(a):
    from .tasks import MANIFEST, build_tasks, freeze, is_frozen
    cfg = load_config()["tasks"]
    if is_frozen() and not a.force:
        print(f"already frozen: {MANIFEST}")
        return 0
    if L.read_rows() and not a.force:
        print("refusing to re-freeze: results already exist for the current task set", file=sys.stderr)
        return 1
    h = freeze(build_tasks(cfg["seed"], cfg["instances_per_type"], cfg["budget_participant_hours"]))
    print(f"frozen {MANIFEST} sha256={h}")
    return 0


def cmd_freeze_wave(a):
    from . import waves as W
    from .planner import pending_items
    cfg = load_config()
    rows = L.read_rows()
    items, _ = pending_items(cfg, rows)
    n_wave = sum(1 for it in items if it.get("wave"))
    nxt = a.wave or W.due(cfg, len(items) - n_wave, n_wave)
    if nxt is None:
        print("no wave due")
        return 0
    print(json.dumps(W.freeze_wave(cfg, nxt)))
    return 0


def cmd_intake(a):
    from .intake import add_to_config, model_line, next_candidate
    from .planner import pending_items
    cfg = load_config()
    items, _ = pending_items(cfg, L.read_rows())
    pick = next_candidate(cfg, len(items))
    if pick is None:
        print(f"no model added ({len(items)} episodes queued)")
        return 0
    c, meta = pick
    line = model_line(c, meta)
    print(f"adding {c['name']} ({meta['gb']} GB, digest {meta['digest'][:12]})")
    if not a.dry_run:
        add_to_config(line)
    gh = os.environ.get("GITHUB_OUTPUT")
    if gh and not a.dry_run:
        with open(gh, "a") as f:
            f.write(f"added={c['name']}\ndigest={meta['digest'][:12]}\n")
    return 0


def cmd_release_notes(a):
    """Print the pending data-release tag (empty if none) and write its notes."""
    s = json.loads((L.LEDGER.parent / "summary.json").read_text())
    tag = s.get("release_tag") or ""
    if tag:
        board = (L.LEDGER.parent.parent / "README.md").read_text()
        i, j = board.find("<!-- leaderboard:start -->"), board.find("<!-- leaderboard:end -->")
        waves = s.get("replication", {}).get("waves", [])
        Path(a.out).write_text(
            f"Data release: the queue drained at {s['generated']}.\n\n"
            f"- {s['episodes_ok']} scored episodes, {s['failed_attempts']} failed attempts logged\n"
            f"- Replication waves completed: {', '.join(map(str, waves)) or 'none yet'}\n"
            f"- Ledger, summary and results report attached; paper PDF and figures on the project page\n\n"
            + (board[i + len("<!-- leaderboard:start -->"):j].strip() if i >= 0 else "") + "\n")
    print(tag)
    gh = os.environ.get("GITHUB_OUTPUT")
    if gh:
        with open(gh, "a") as f:
            f.write(f"tag={tag}\n")
    return 0


def cmd_plan(a):
    from .planner import make_plan
    plan = make_plan(load_config(), L.read_rows())
    Path(a.out).write_text(json.dumps(plan, indent=2))
    print(json.dumps({"setup": plan["setup"], "pending": plan["n_pending_total"],
                      "shards": len(plan["shards"]), "gates": {k: v["passed"] for k, v in plan["gates"].items()}}))
    gh = os.environ.get("GITHUB_OUTPUT")
    if gh:
        with open(gh, "a") as f:
            f.write(f"matrix={json.dumps(plan['matrix'])}\n")
            f.write(f"has_work={'true' if plan['matrix'] else 'false'}\n")
            f.write(f"setup={','.join(plan['setup'])}\n")
    return 0


def cmd_run(a):
    from .runner import run_shard
    plan = json.loads(Path(a.plan).read_text())
    stats = run_shard(plan, a.shard, Path(a.out), a.budget_min, load_config())
    print(json.dumps(stats))
    return 0


def cmd_collect(a):
    print(f"collected {L.collect()} new rows")
    return 0


def cmd_report(a):
    from .report import build
    out = build()
    print(json.dumps({"episodes_ok": out["episodes_ok"], "queued": out["queued"]}))
    return 0


def cmd_figures(a):
    from .animate import build_all as anims
    from .figures import build_all as figs
    out = figs() + ([] if a.no_animations else anims())
    print("\n".join(out) or "no figures (no data yet)")
    return 0


def cmd_paper_tables(a):
    from .paper import build
    print("\n".join(build()))
    return 0


def cmd_smoke(a):
    """Fast end-to-end check with baselines only (no LLM, no ERP CORE needed)."""
    from .agents import baselines as B
    from .env import LabEnv
    from .scoring import score
    from .tasks import build_tasks
    params = load_params()
    tasks = build_tasks(1, 1, 30.0)
    for t in tasks:
        env = LabEnv(t, params, "synthetic", "named", 0)
        B.run_scripted(env, 0)
        s = score(env.episode.submitted, t.mechanism.truth(), t.task_type)
        print(f"{t.task_id:22s} scripted exact={s['exact']:.0f} edge_acc={s['edge_acc']:.2f}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="axiom")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("fit-erpcore"); s.add_argument("--participants", type=int, default=40); s.set_defaults(f=cmd_fit)
    s = sub.add_parser("oracle"); s.add_argument("--sims", type=int, default=8); s.set_defaults(f=cmd_oracle)
    s = sub.add_parser("freeze"); s.add_argument("--force", action="store_true"); s.set_defaults(f=cmd_freeze)
    s = sub.add_parser("bio-setup"); s.add_argument("--force", action="store_true"); s.set_defaults(f=cmd_bio_setup)
    s = sub.add_parser("plan"); s.add_argument("--out", default="plan.json"); s.set_defaults(f=cmd_plan)
    s = sub.add_parser("run")
    s.add_argument("--plan", default="plan.json"); s.add_argument("--shard", type=int, required=True)
    s.add_argument("--out", required=True); s.add_argument("--budget-min", type=float, default=320)
    s.set_defaults(f=cmd_run)
    s = sub.add_parser("freeze-wave"); s.add_argument("--wave", type=int); s.set_defaults(f=cmd_freeze_wave)
    s = sub.add_parser("intake"); s.add_argument("--dry-run", action="store_true"); s.set_defaults(f=cmd_intake)
    s = sub.add_parser("release-notes"); s.add_argument("--out", default="release-notes.md")
    s.set_defaults(f=cmd_release_notes)
    sub.add_parser("collect").set_defaults(f=cmd_collect)
    sub.add_parser("report").set_defaults(f=cmd_report)
    s = sub.add_parser("figures"); s.add_argument("--no-animations", action="store_true"); s.set_defaults(f=cmd_figures)
    sub.add_parser("paper-tables").set_defaults(f=cmd_paper_tables)
    sub.add_parser("smoke").set_defaults(f=cmd_smoke)
    a = p.parse_args(argv)
    return a.f(a)


if __name__ == "__main__":
    sys.exit(main())
