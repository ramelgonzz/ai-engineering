"""
Orchestrator: write -> test -> read failure -> patch, looping until tests
pass or the iteration budget runs out.

Key design choice: it tracks the BEST attempt seen (most tests passing),
not just the last one. If the budget runs out, it rolls back to that best
version rather than leaving whatever the final, possibly-worse attempt
was sitting in the file. An agent that can regress and not notice is
worse than one that plateaus.
"""
from pathlib import Path

from agent import coder, executor
from agent.trace import Trace
from config import MAX_CODE_ITERATIONS


def run(task: str, workspace_dir: str, solution_file: str = "solution.py") -> dict:
    trace = Trace(task)
    solution_path = Path(workspace_dir) / solution_file

    current_code = solution_path.read_text() if solution_path.exists() else ""
    best_code = current_code
    best_passed_count = -1
    last_test_output = None
    final_status = "failed"
    rolled_back = False

    for attempt in range(1, MAX_CODE_ITERATIONS + 1):
        code, usage = coder.write_solution(task, current_code, last_test_output)
        solution_path.write_text(code)
        current_code = code

        result = executor.run_tests(workspace_dir)
        trace.log_attempt(attempt, result, usage)

        if result["passed"]:
            best_code = code
            final_status = "passed"
            break

        if result["passed_count"] > best_passed_count:
            best_passed_count = result["passed_count"]
            best_code = code

        last_test_output = result["output"]
    else:
        # Budget exhausted without a full pass — roll back to the best
        # attempt seen, not whatever the last (possibly worse) one was.
        if current_code != best_code:
            solution_path.write_text(best_code)
            rolled_back = True
        final_status = "budget_exhausted"

    trace_path = trace.finish(final_status, rolled_back)
    return {
        "status": final_status,
        "rolled_back": rolled_back,
        "final_code": best_code,
        "trace_path": str(trace_path),
    }
