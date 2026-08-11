"""
Planner: turns a question (plus, on later rounds, critique feedback about
what's missing) into a short list of concrete search queries.

This is kept as its own LLM call — separate from the search tool call
itself — so the reasoning ("what do I still need to know") is visible in
the trace and testable independently of the search API.
"""
import json

from anthropic import Anthropic

from config import ANTHROPIC_API_KEY, MODEL_NAME

client = Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are the planning step of a research agent.
Given a research question — and optionally, feedback about gaps in a
previous draft — output 2-4 concrete, specific web search queries that
would help answer it.

Respond with ONLY a JSON object, no other text:
{"reasoning": "<one sentence on your search strategy>", "queries": ["...", "..."]}
"""


def plan(question: str, gap_feedback: str | None = None) -> tuple[list[str], object]:
    user_msg = question
    if gap_feedback:
        user_msg += f"\n\nA previous draft had these gaps — search to fill them:\n{gap_feedback}"

    resp = client.messages.create(
        model=MODEL_NAME,
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    raw = resp.content[0].text
    parsed = _safe_json(raw)
    return parsed.get("queries", []), resp.usage


def _safe_json(raw: str) -> dict:
    """LLMs occasionally wrap JSON in prose or code fences despite
    instructions — strip that defensively rather than crashing the run."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`").removeprefix("json").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"queries": []}
