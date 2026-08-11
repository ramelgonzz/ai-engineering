"""
Critic: reviews the draft against the original question and decides
whether the agent should search again or is done.

This is the step that makes the system "agentic" rather than a fixed
pipeline — it's the agent deciding, on its own, whether its work is good
enough. Keep it strict: a critic that always says "complete" is decoration.
"""
import json

from anthropic import Anthropic

from config import ANTHROPIC_API_KEY, MODEL_NAME

client = Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are the critique step of a research agent. Review the
draft against the original question. Be genuinely critical — vague or
generic drafts should not pass.

Respond with ONLY a JSON object, no other text:
{"complete": true/false, "confidence": 0.0-1.0, "gaps": "<what's missing, or empty string if none>"}
"""


def critique(question: str, draft: str) -> tuple[dict, object]:
    user_msg = f"Question: {question}\n\nDraft:\n{draft}"

    resp = client.messages.create(
        model=MODEL_NAME,
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.strip("`").removeprefix("json").strip()
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Fail closed: if we can't parse the critique, treat it as complete
        # rather than risk an infinite loop on a malformed response.
        result = {"complete": True, "confidence": 0.0, "gaps": ""}
    return result, resp.usage
