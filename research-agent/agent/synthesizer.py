"""
Synthesizer: turns collected source text into a draft report with inline
citations like [1], [2] mapping to a source list.
"""
from anthropic import Anthropic

from config import ANTHROPIC_API_KEY, MODEL_NAME

client = Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are the synthesis step of a research agent.
Write a clear, well-organized answer to the research question using ONLY
the provided sources. Cite claims inline as [1], [2] etc. matching the
source numbers given. If sources conflict, say so. Do not invent facts
not present in the sources.
"""


def synthesize(question: str, sources: list[dict]) -> tuple[str, object]:
    source_block = "\n\n".join(
        f"[{i+1}] {s['title']} ({s['url']})\n{s['text']}"
        for i, s in enumerate(sources)
    )
    user_msg = f"Question: {question}\n\nSources:\n{source_block}"

    resp = client.messages.create(
        model=MODEL_NAME,
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    return resp.content[0].text, resp.usage
