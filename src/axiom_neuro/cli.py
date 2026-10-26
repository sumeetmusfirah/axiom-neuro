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
    sub.add_parser("collect").set_defaults(f=cmd_collect)
    sub.add_parser("report").set_defaults(f=cmd_report)
    s = sub.add_parser("figures"); s.add_argument("--no-animations", action="store_true"); s.set_defaults(f=cmd_figures)
    sub.add_parser("paper-tables").set_defaults(f=cmd_paper_tables)
    sub.add_parser("smoke").set_defaults(f=cmd_smoke)
    a = p.parse_args(argv)
    return a.f(a)


if __name__ == "__main__":
    sys.exit(main())
