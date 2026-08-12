# Code-fixing agent

A self-correcting coding agent: write code → run tests in a sandboxed
subprocess → read the failure output → patch → repeat, with a hard
iteration cap and rollback to the best attempt if the budget runs out.

## Architecture

```
Task spec + current code
        |
        v
    Coder (LLM) --------------------+
        |                           |
        v                           |
  Run tests (subprocess,            |
  hard timeout)                     |
        |                           |
        v                           |
   Tests pass? --(no, budget left)--+
        |
    (yes) or (budget exhausted -> rollback to best attempt)
        |
        v
   Final solution file
```

- **Coder** (`agent/coder.py`) — LLM call that rewrites the solution file
  given the task, current code, and (after attempt 1) the last test
  failure output.
- **Executor** (`agent/executor.py`) — runs pytest in a subprocess with a
  hard timeout, so generated code that hangs (e.g. an infinite loop)
  can't take the orchestrator down with it. Parses pass/fail counts from
  pytest's summary line.
- **Orchestrator** (`agent/orchestrator.py`) — the loop itself. Tracks the
  best attempt seen (most tests passing), not just the last one, and
  rolls back to it if the iteration budget is exhausted without a full
  pass. This is the main design decision in this project: an agent that
  can silently regress on its last attempt is worse than one that
  plateaus and says so.
- **Trace** (`agent/trace.py`) — logs every attempt (pass/fail counts,
  tokens) to `traces/<run_id>.json`.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in ANTHROPIC_API_KEY
python cli.py example_task/task.md example_task
```

The example task asks the agent to implement a duration-string parser
(`"1h30m" -> 5400`) against `example_task/test_solution.py`. The starting
`solution.py` deliberately raises `NotImplementedError` so the first run
demonstrates the loop actually converging, not just passing on attempt 1.

## Guardrails (and why they're here)

- **`MAX_CODE_ITERATIONS` (default 5)** — hard cap on write/test cycles.
- **`TEST_TIMEOUT_SECONDS` (default 10)** — subprocess timeout per test
  run, so a generated infinite loop fails fast instead of hanging the
  agent indefinitely.
- **Rollback to best attempt** — if the budget runs out, the file on disk
  is the best-scoring version seen, not necessarily the last one
  generated. The trace records whether a rollback happened.

## Known limitations

- Full-file rewrite per attempt, not targeted diffs — fine for small
  files like this one, but wouldn't scale to a large codebase without
  switching to patch-based edits.
- Single test file, single solution file — no multi-file project support.
- No sandboxing beyond subprocess isolation (no container, no restricted
  filesystem/network access for the generated code itself). Fine for a
  portfolio demo; a production version would run generated code in a
  more locked-down sandbox.

## TODO

- pytest
- Multi-file project support (point it at a whole repo, not one file)
- Static analysis pass (ruff/mypy) before running tests, to catch cheap
  errors without burning a full test-run + LLM round trip
- A diff-based coder mode for larger files
- UI
