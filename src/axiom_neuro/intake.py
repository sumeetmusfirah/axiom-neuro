"""Model intake: add the next candidate model to the study when the queue runs short.

Candidates are listed in `configs/experiment.toml` under [intake], in the order they should
enter. A candidate is added only if its weights exist in the Ollama registry and fit on a free
runner. It is added with the exact registry digest, so the weights it was benchmarked on stay
recorded even if the tag moves later. Models added this way are marked `added = <date>`
and reported as post-registration additions. The preregistered hypotheses use only the
original models.
"""

from __future__ import annotations

import hashlib
import json
import re
import urllib.error
import urllib.request
from datetime import date

from .config import CONFIG

REGISTRY = "https://registry.ollama.ai/v2/library/{repo}/manifests/{tag}"
ACCEPT = "application/vnd.docker.distribution.manifest.v2+json"


def registry_info(name: str, timeout: int = 30) -> dict | None:
    """Download size and digest of a model tag, or None if the tag does not exist."""
    repo, _, tag = name.partition(":")
    req = urllib.request.Request(REGISTRY.format(repo=repo, tag=tag or "latest"), headers={"Accept": ACCEPT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    layers = json.loads(body).get("layers", [])
    # Ollama names a model build by the sha256 of its manifest (what `ollama list` shows).
    return {"gb": round(sum(layer["size"] for layer in layers) / 1e9, 2),
            "digest": hashlib.sha256(body).hexdigest()}


def minutes_per_episode(params_b: float) -> int:
    # CPU estimate matching the hand-set values for the original models (~1.5 min per B params).
    return max(5, round(1.5 * params_b))


def next_candidate(cfg: dict, queued: int, info=registry_info) -> tuple[dict, dict] | None:
    ic = cfg.get("intake", {})
    if not ic.get("enabled") or queued >= ic["max_queue_episodes"]:
        return None
    have = {m["name"] for m in cfg["llm"]["models"]}
    for c in ic["candidates"]:
        if c["name"] in have:
            continue
        meta = info(c["name"])
        if meta and meta["gb"] <= ic["max_download_gb"]:
            return c, meta
    return None


def model_line(c: dict, meta: dict, today: date | None = None) -> str:
    return (f'  {{ name = "{c["name"]}", params_b = {c["params_b"]}, '
            f'minutes_per_episode = {minutes_per_episode(c["params_b"])}, '
            f'added = "{(today or date.today()).isoformat()}", digest = "{meta["digest"][:12]}" }},\n')


def add_to_config(line: str, path=CONFIG) -> None:
    """Insert one model line at the end of [llm].models, leaving the rest of the file untouched."""
    text = path.read_text()
    m = re.search(r"^\[llm\]\s*\n.*?^models = \[\n(.*?)^\]", text, flags=re.S | re.M)
    if not m:
        raise ValueError("could not find [llm] models = [ ... ] in config")
    path.write_text(text[:m.end(1)] + line + text[m.end(1):])
