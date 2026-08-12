"""
Executor: runs pytest against the current solution file in a subprocess.

Subprocess isolation (rather than exec()-ing generated code in-process)
matters here: generated code can be wrong in ways that hang or crash, and
a subprocess with a timeout can't take the orchestrator down with it.
"""
import re
import subprocess

from config import TEST_TIMEOUT_SECONDS


def run_tests(workspace_dir: str, test_file: str = "test_solution.py") -> dict:
    """Runs pytest in workspace_dir. Returns pass/fail counts and raw output.

    Never raises on test failure — a failing run is a normal, expected
    result the orchestrator acts on, not an error condition.
    """
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", test_file, "-q", "--tb=short"],
            cwd=workspace_dir,
            capture_output=True,
            text=True,
            timeout=TEST_TIMEOUT_SECONDS,
        )
        output = result.stdout + result.stderr
        passed_count, failed_count = _parse_summary(output)
        return {
            "passed": result.returncode == 0,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "output": output[-3000:],  # keep prompts bounded on large failures
        }
    except subprocess.TimeoutExpired:
        return {
            "passed": False,
            "passed_count": 0,
            "failed_count": None,
            "output": f"[timed out after {TEST_TIMEOUT_SECONDS}s — likely an infinite loop]",
        }


def _parse_summary(output: str) -> tuple[int, int]:
    """Pulls counts out of pytest's summary line, e.g. '3 passed, 2 failed'."""
    passed = re.search(r"(\d+) passed", output)
    failed = re.search(r"(\d+) failed", output)
    return (
        int(passed.group(1)) if passed else 0,
        int(failed.group(1)) if failed else 0,
    )
