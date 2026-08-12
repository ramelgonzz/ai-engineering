"""
Coder: given the task spec, the current solution code, and (after the
first attempt) the last test failure output, produces a full rewrite of
the solution file.

Full-file rewrite rather than diffs — simpler to reason about and to
verify (no diff-application edge cases), and the files this agent targets
are small enough that it's cheap. A production version working on large
files would switch to targeted patches.
"""
from anthropic import Anthropic

from config import ANTHROPIC_API_KEY, MODEL_NAME

client = Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are the coding step of a self-correcting code agent.
Given a task, the current code, and (if present) the last test failure
output, output the COMPLETE new contents of the solution file that fixes
the failures.

Rules:
- Output ONLY raw Python code — no markdown fences, no explanation.
- Keep the same function/class names the tests expect.
- Fix the actual cause of the failure, don't just special-case the test input.
"""


def write_solution(
    task: str, current_code: str, last_test_output: str | None
) -> tuple[str, object]:
    user_msg = f"Task:\n{task}\n\nCurrent code:\n{current_code}"
    if last_test_output:
        user_msg += f"\n\nLast test run output:\n{last_test_output}"

    resp = client.messages.create(
        model=MODEL_NAME,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    code = resp.content[0].text.strip()
    if code.startswith("```"):
        code = code.strip("`")
        if code.startswith("python"):
            code = code[len("python"):].strip()
    return code, resp.usage
