"""
Orchestrator: wires planner -> search -> extract -> synthesizer -> critic
into a loop, with a hard cap so a confused agent can't run forever.

The CLI with the query calls the orchestrator which ties everything together
with a MAX_PLAN_ITERATIONS for the for loop, defined in config.py.
"""
from agent import planner, synthesizer, critic, tools
from agent.trace import Trace
from config import MAX_PLAN_ITERATIONS, MAX_SOURCES_TOTAL


def run(question: str) -> tuple[str, str]:
    trace = Trace(question)
    all_sources = []
    gap_feedback = None
    draft = ""

    for iteration in range(1, MAX_PLAN_ITERATIONS + 1):
        queries, usage = planner.plan(question, gap_feedback)
        trace.log("plan", {"iteration": iteration, "queries": queries}, usage)

        if not queries:
            break  # planner found nothing left to search for

        for q in queries:
            if len(all_sources) >= MAX_SOURCES_TOTAL:
                break
            for hit in tools.search_web(q):
                if len(all_sources) >= MAX_SOURCES_TOTAL:
                    break
                text = tools.fetch_and_extract(hit["url"])
                all_sources.append({**hit, "text": text})
                trace.log("fetch", {"url": hit["url"], "chars": len(text)})

        draft, usage = synthesizer.synthesize(question, all_sources)
        trace.log("synthesize", {"draft_len": len(draft)}, usage)

        verdict, usage = critic.critique(question, draft)
        trace.log("critique", verdict, usage)

        if verdict.get("complete"):
            break
        gap_feedback = verdict.get("gaps")
    else:
        # Loop exhausted without a "complete" verdict — ship what we have,
        # but say so rather than presenting it as fully verified.
        draft += "\n\n*Note: research budget reached before all gaps were resolved.*"

    trace_path = trace.finish(draft)
    return draft, str(trace_path)
