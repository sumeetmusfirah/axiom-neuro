"""A local LLM as the scientist. One JSON action per turn, constrained by a schema."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Protocol

from ..env import ACTIONS

def action_schema(actions=ACTIONS) -> dict:
    return {
        "type": "object",
        "properties": {
            "thought": {"type": "string"},
            "action": {"type": "string", "enum": list(actions)},
            "args": {"type": "object"},
        },
        "required": ["thought", "action", "args"],
    }


ACTION_SCHEMA = action_schema()

PROTOCOL = """
Reply with ONE JSON object per turn: {"thought": "<one or two sentences>", "action": "<name>", "args": {...}}

Actions and their args:
  design_experiment  {"factors": ["L","S"], "fixed": {"L": 1}, "assignment": "within", "order": "counterbalanced",
                      "n_participants": 24, "trials_per_cell": 80, "eeg": false, "ica": false}   (spends budget)
  describe           {"datasets": ["D0","D1"]}                       cell means
  regress            {"datasets": ["D1"], "outcome": "rt"|"accuracy"|"theta"|"blink",
                      "predictors": ["L","S","SxL","practice"], "exclude_blinks": false}
  order_check        {"dataset": "D0"}                              is any factor tied to session order?
  artifact_check     {"dataset": "D1"}                              blink rates and blink-free theta (EEG only)
  submit             {"edges": {"L->Y": {"present": true, "confidence": 0.9}, ... all six edges ...}}
                     confidence = your probability (0.5-1.0) that your present/absent call is right.

You have a limited number of turns. Analysis is free; experiments cost budget. Submit before turns run out.
""".strip()


class ChatClient(Protocol):
    def chat(self, messages: list[dict], seed: int, actions=ACTIONS) -> str: ...


class OllamaClient:
    def __init__(self, model: str, temperature: float = 0.7, num_predict: int = 400,
                 timeout_s: int = 600, host: str | None = None):
        self.model = model
        self.temperature = temperature
        self.num_predict = num_predict
        self.timeout_s = timeout_s
        self.host = host or os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
        if not self.host.startswith("http"):
            self.host = "http://" + self.host

    def digest(self) -> str | None:
        """The exact weights being run, so every ledger row names the model build it used."""
        try:
            with urllib.request.urlopen(f"{self.host}/api/tags", timeout=30) as r:
                tags = json.loads(r.read())["models"]
        except (urllib.error.URLError, OSError, KeyError, ValueError):
            return None
        return next((m.get("digest") for m in tags if m.get("name") == self.model), None)

    def chat(self, messages: list[dict], seed: int, actions=ACTIONS) -> str:
        body = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "format": action_schema(actions),
            "think": False,
            "options": {"temperature": self.temperature, "seed": seed,
                        "num_predict": self.num_predict, "num_ctx": 8192},
        }
        req = urllib.request.Request(f"{self.host}/api/chat", data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout_s) as r:
            return json.loads(r.read())["message"]["content"]


class QuotaExhausted(RuntimeError):
    """The hosted provider's daily free quota is used up: stop the shard; the work is re-planned later."""


class OpenRouterClient:
    """A hosted open-weight model through OpenRouter (free tier: about 50 requests a day per account,
    20 a minute). Hosted weights cannot be pinned by digest, so each row records the model id and the
    provider that actually served it."""
    URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, model: str, temperature: float = 0.7, max_tokens: int = 1500,
                 timeout_s: int = 300, min_interval_s: float = 3.5):
        self.model, self.temperature, self.max_tokens = model, temperature, max_tokens
        self.timeout_s, self.min_interval_s = timeout_s, min_interval_s
        self.key = os.environ.get("OPENROUTER_API_KEY", "")
        self.served: str | None = None
        self._last = 0.0

    def digest(self) -> str | None:
        return self.served

    def chat(self, messages: list[dict], seed: int, actions=ACTIONS) -> str:
        import time
        if not self.key:
            raise QuotaExhausted("OPENROUTER_API_KEY is not set")
        body = {"model": self.model, "messages": messages, "temperature": self.temperature,
                "seed": seed, "max_tokens": self.max_tokens}
        for attempt in range(6):
            wait = self.min_interval_s - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()
            req = urllib.request.Request(self.URL, data=json.dumps(body).encode(), headers={
                "Content-Type": "application/json", "Authorization": f"Bearer {self.key}",
                "X-Title": "axiom-neuro"})
            try:
                with urllib.request.urlopen(req, timeout=self.timeout_s) as r:
                    out = json.loads(r.read())
            except urllib.error.HTTPError as e:
                text = e.read().decode(errors="replace")[:500]
                if e.code == 429 and "day" in text.lower():
                    raise QuotaExhausted(text) from e
                if e.code in (429, 500, 502, 503, 504) and attempt < 5:
                    time.sleep(10 * (attempt + 1))
                    continue
                raise RuntimeError(f"OpenRouter {e.code}: {text}") from e
            except (urllib.error.URLError, TimeoutError, OSError):
                if attempt < 5:
                    time.sleep(10 * (attempt + 1))
                    continue
                raise
            if "error" in out:
                msg = json.dumps(out["error"])[:500]
                if "day" in msg.lower() and "limit" in msg.lower():
                    raise QuotaExhausted(msg)
                if attempt < 5:
                    time.sleep(10 * (attempt + 1))
                    continue
                raise RuntimeError(f"OpenRouter error: {msg}")
            self.served = f"{out.get('model', self.model)}@{out.get('provider', '?')}"
            return out["choices"][0]["message"].get("content") or ""
        raise RuntimeError("OpenRouter: no reply after retries")


def parse_action(text: str, actions=ACTIONS) -> tuple[str, dict, str]:
    s = text.strip()
    if "</think>" in s:  # some builds still emit reasoning; keep only the answer
        s = s.split("</think>", 1)[1]
    start, end = s.find("{"), s.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("no JSON object in reply")
    obj = json.loads(s[start:end + 1])
    action = obj.get("action")
    if action not in actions:
        raise ValueError(f"action must be one of {list(actions)}")
    args = obj.get("args") or {}
    if not isinstance(args, dict):
        raise ValueError("args must be an object")
    return action, args, str(obj.get("thought", ""))[:500]


def run_llm(env, client: ChatClient, seed: int, max_turns: int = 12, instruction: str = "") -> dict:
    """Run one episode in any lab (neuro or bio). The env holds actions and the submission.
    ``instruction`` (author studies only) is appended to the system prompt."""
    actions = getattr(env, "ACTIONS", ACTIONS)
    protocol = env.protocol() if hasattr(env, "protocol") else PROTOCOL
    messages = [
        {"role": "system", "content": "You are a careful experimental scientist. " + protocol
         + (f"\n\nAdditional instruction: {instruction}" if instruction else "")},
        {"role": "user", "content": env.briefing() + "\n\nTurn 1 of " + str(max_turns) + ". Your move."},
    ]
    parse_failures, consecutive = 0, 0
    turns = 0
    for turn in range(1, max_turns + 1):
        turns = turn
        reply = client.chat(messages, seed=seed * 1000 + turn, actions=actions)
        messages.append({"role": "assistant", "content": reply})
        try:
            action, args, thought = parse_action(reply, actions)
            consecutive = 0
        except (ValueError, json.JSONDecodeError) as exc:
            parse_failures += 1
            consecutive += 1
            if consecutive >= 3:
                break
            messages.append({"role": "user", "content": f"Invalid reply ({exc}). Reply with one JSON object."})
            continue
        obs = env.step(action, args)
        env.episode.actions[-1]["thought"] = thought
        if env.episode.submitted is not None:
            break
        left = max_turns - turn
        nudge = " This is your LAST turn: you must submit now." if left == 1 else ""
        messages.append({"role": "user", "content":
                         f"Observation: {json.dumps(obs)}\nRemaining budget: {env.remaining} {getattr(env, 'BUDGET_UNIT', 'participant-hours')}. "
                         f"Turns left: {left}.{nudge}"})
    submitted = env.episode.submitted is not None
    if not submitted:
        env.submit({})  # all edges "absent" at 0.5: scored, and flagged as no-submit
    return {"turns": turns, "parse_failures": parse_failures, "submitted": submitted,
            "transcript": messages}
