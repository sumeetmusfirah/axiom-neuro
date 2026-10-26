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


def run_llm(env, client: ChatClient, seed: int, max_turns: int = 12) -> dict:
    """Run one episode in any lab (neuro or bio). The env holds actions and the submission."""
    actions = getattr(env, "ACTIONS", ACTIONS)
    protocol = env.protocol() if hasattr(env, "protocol") else PROTOCOL
    messages = [
        {"role": "system", "content": "You are a careful experimental scientist. " + protocol},
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
                         f"Observation: {json.dumps(obs)}\nRemaining budget: {env.remaining} participant-hours. "
                         f"Turns left: {left}.{nudge}"})
    submitted = env.episode.submitted is not None
    if not submitted:
        env.submit({})  # all edges "absent" at 0.5: scored, and flagged as no-submit
    return {"turns": turns, "parse_failures": parse_failures, "submitted": submitted,
            "transcript": messages}
