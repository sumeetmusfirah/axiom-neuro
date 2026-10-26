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
    seen = {}
    for r in rows:
        if r["status"] == "ok":
            seen[r["key"]] = r
    return list(seen.values())


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
