"""
Central config. Loads from a .env file (see .env.example) or real env vars.
Keeping this in one place makes it obvious what the agent depends on.
MAX_PLAN_ITERATIONS set so the orchestrator can note if budget runs out
instead of presenting incomplete work.
"""
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")  # https://tavily.com — free tier available

MODEL_NAME = os.getenv("MODEL_NAME", "claude-sonnet-4-6")

# Guardrails — these exist so a stuck agent can't loop forever or blow up cost.
MAX_PLAN_ITERATIONS = int(os.getenv("MAX_PLAN_ITERATIONS", 3))
MAX_SEARCH_RESULTS_PER_QUERY = int(os.getenv("MAX_SEARCH_RESULTS_PER_QUERY", 4))
MAX_SOURCES_TOTAL = int(os.getenv("MAX_SOURCES_TOTAL", 15))

if not ANTHROPIC_API_KEY:
    raise RuntimeError(
        "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and fill it in."
    )
