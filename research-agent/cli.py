"""
Usage:
    python cli.py "What are the main risks of quantum computing for RSA encryption?"
"""
import argparse

from agent.orchestrator import run


def main():
    parser = argparse.ArgumentParser(description="Research agent")
    parser.add_argument("question", help="The research question to answer")
    args = parser.parse_args()

    report, trace_path = run(args.question)

    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)
    print(f"\nFull trace: {trace_path}")


if __name__ == "__main__":
    main()
