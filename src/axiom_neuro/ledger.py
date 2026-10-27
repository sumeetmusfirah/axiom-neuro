"""Append-only results ledger. One JSON row per episode attempt; idempotent by key."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .params import REPO

LEDGER = REPO / "results" / "ledger.jsonl"
INCOMING = REPO / "results" / "incoming"


def item_key(task_id: str, agent: str, model: str, track: str, labels: str, seed: int) -> str:
    return f"{task_id}|{agent}|{model}|{track}|{labels}|{seed}"


def read_rows(path: Path = LEDGER) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def status(rows: list[dict], max_errors: int) -> tuple[set, Counter]:
    """Keys that need no more work (ok, or failed too often) and per-key error counts."""
    ok = {r["key"] for r in rows if r["status"] == "ok"}
    errors = Counter(r["key"] for r in rows if r["status"] == "error")
    done = ok | {k for k, n in errors.items() if n >= max_errors}
    return done, errors


def ok_rows(rows: list[dict]) -> list[dict]:
    """One scored row per item: the first attempt to complete. Later duplicates (re-runs of an
    item that had already finished) never replace it; they are used only by `duplicate_pairs`."""
    seen = {}
    for r in sorted((r for r in rows if r["status"] == "ok"), key=lambda r: r.get("finished_at", "")):
        seen.setdefault(r["key"], r)
    return list(seen.values())


def duplicate_pairs(rows: list[dict]) -> list[tuple[dict, dict]]:
    """(first, second) completed attempts of the same item: same task, agent, model, track, labels, seed."""
    by = {}
    for r in sorted((r for r in rows if r["status"] == "ok"), key=lambda r: r.get("finished_at", "")):
        by.setdefault(r["key"], []).append(r)
    return [(v[0], v[1]) for v in by.values() if len(v) > 1]


def primary(rows: list[dict]) -> list[dict]:
    """The preregistered study only. Replication-wave rows (``wave`` >= 1) and author studies
    (``study``) are analysed separately."""
    return [r for r in rows if not r.get("wave") and not r.get("study")]


def collect(incoming: Path = INCOMING, path: Path = LEDGER) -> int:
    """Merge shard outputs into the ledger. Returns number of new rows."""
    rows = read_rows(path)
    seen = {(r["key"], r.get("attempt_id")) for r in rows}
    new = 0
    for f in sorted(incoming.rglob("*.jsonl")) if incoming.exists() else []:
        for line in f.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if (r["key"], r.get("attempt_id")) in seen:
                continue
            seen.add((r["key"], r.get("attempt_id")))
            rows.append(r)
            new += 1
    rows.sort(key=lambda r: (r["key"], r.get("finished_at", "")))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
    return new
