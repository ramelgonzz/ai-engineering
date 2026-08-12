"""
Usage:
    python cli.py example_task/task.md example_task

Runs the write/test/patch loop against the given task spec and workspace
directory (which must contain a test_solution.py and, optionally, a
starting solution.py).
"""
import argparse
from pathlib import Path

from agent.orchestrator import run


def main():
    parser = argparse.ArgumentParser(description="Code-fixing agent")
    parser.add_argument("task_file", help="Path to a markdown/text file describing the task")
    parser.add_argument("workspace", help="Directory containing test_solution.py")
    args = parser.parse_args()

    task = Path(args.task_file).read_text()
    result = run(task, args.workspace)

    print("\n" + "=" * 60)
    print(f"Status: {result['status']}  (rolled back: {result['rolled_back']})")
    print("=" * 60)
    print(result["final_code"])
    print(f"\nFull trace: {result['trace_path']}")


if __name__ == "__main__":
    main()
