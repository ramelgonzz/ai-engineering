"""
Trace logging.

This is the piece most tutorials skip and most interviewers ask about.
Every step the agent takes gets recorded: what it decided, what it called,
what it cost. Without this, "the agent is reasoning" is just a claim —
with it, it's something you can show.
"""
import json
import time
import uuid
from pathlib import Path

TRACE_DIR = Path(__file__).parent.parent / "traces"
TRACE_DIR.mkdir(exist_ok=True)


class Trace:
    def __init__(self, question: str):
        self.run_id = str(uuid.uuid4())[:8]
        self.question = question
        self.started_at = time.time()
        self.steps = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def log(self, step_type: str, detail: dict, usage=None):
        """Record one step. usage is an Anthropic API usage object, if this
        step made an LLM call — used to track running token cost."""
        entry = {
            "t": round(time.time() - self.started_at, 2),
            "step": step_type,
            "detail": detail,
        }
        if usage:
            entry["tokens"] = {"in": usage.input_tokens, "out": usage.output_tokens}
            self.total_input_tokens += usage.input_tokens
            self.total_output_tokens += usage.output_tokens
        self.steps.append(entry)
        print(f"[{entry['t']:>6}s] {step_type}: {_summarize(detail)}")

    def finish(self, final_report: str):
        self.finished_at = time.time()
        payload = {
            "run_id": self.run_id,
            "question": self.question,
            "duration_s": round(self.finished_at - self.started_at, 2),
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            # Sonnet pricing as of this writing — update if it changes.
            "estimated_cost_usd": round(
                self.total_input_tokens / 1_000_000 * 3
                + self.total_output_tokens / 1_000_000 * 15,
                4,
            ),
            "steps": self.steps,
            "final_report": final_report,
        }
        out_path = TRACE_DIR / f"{self.run_id}.json"
        out_path.write_text(json.dumps(payload, indent=2))
        print(f"\nTrace written to {out_path}")
        print(
            f"Total: {self.total_input_tokens} in / {self.total_output_tokens} out "
            f"tokens, ~${payload['estimated_cost_usd']}"
        )
        return out_path


def _summarize(detail: dict) -> str:
    """One-line summary for console output so a run is readable live."""
    if "queries" in detail:
        return f"{len(detail['queries'])} queries — {detail['queries']}"
    if "url" in detail:
        return detail["url"]
    if "complete" in detail:
        return f"complete={detail['complete']}, gaps={detail.get('gaps')}"
    return str(detail)[:120]
