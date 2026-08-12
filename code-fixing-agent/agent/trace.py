"""
Trace logging — same pattern as the research agent's trace.py. Every
attempt gets recorded so a "the agent converged in 3 attempts" claim is
backed by a file, not just an anecdote.
"""
import json
import time
import uuid
from pathlib import Path

TRACE_DIR = Path(__file__).parent.parent / "traces"
TRACE_DIR.mkdir(exist_ok=True)


class Trace:
    def __init__(self, task: str):
        self.run_id = str(uuid.uuid4())[:8]
        self.task = task
        self.started_at = time.time()
        self.attempts = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def log_attempt(self, attempt_num: int, test_result: dict, usage=None):
        entry = {
            "attempt": attempt_num,
            "t": round(time.time() - self.started_at, 2),
            "passed": test_result["passed"],
            "passed_count": test_result["passed_count"],
            "failed_count": test_result["failed_count"],
        }
        if usage:
            entry["tokens"] = {"in": usage.input_tokens, "out": usage.output_tokens}
            self.total_input_tokens += usage.input_tokens
            self.total_output_tokens += usage.output_tokens
        self.attempts.append(entry)
        status = "PASSED" if entry["passed"] else f"{entry['passed_count']} passed / {entry['failed_count']} failed"
        print(f"[attempt {attempt_num}] {status}")

    def finish(self, final_status: str, rolled_back: bool):
        payload = {
            "run_id": self.run_id,
            "task": self.task,
            "final_status": final_status,
            "rolled_back_to_best_attempt": rolled_back,
            "num_attempts": len(self.attempts),
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "estimated_cost_usd": round(
                self.total_input_tokens / 1_000_000 * 3
                + self.total_output_tokens / 1_000_000 * 15,
                4,
            ),
            "attempts": self.attempts,
        }
        out_path = TRACE_DIR / f"{self.run_id}.json"
        out_path.write_text(json.dumps(payload, indent=2))
        print(f"\nTrace written to {out_path}")
        return out_path
