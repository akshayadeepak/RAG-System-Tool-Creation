"""
Automated evaluation runner for the Northstar Insights RAG assistant.

Runs all 16 evaluation questions from the assignment brief through the pipeline,
captures routing decisions, tool calls, and answers, and writes results to "results/evaluation_raw.json".

Usage:
    python run_evaluation.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent / "results"
OUTPUT_DIR.mkdir(exist_ok=True)

RAW_OUTPUT_PATH = OUTPUT_DIR / "evaluation_raw.json"

EVALUATION_QUESTIONS = [
    # Basic Retrieval
    {"id": 1, "category": "Basic Retrieval", "query": "How many PTO days do full-time employees receive?"},
    {"id": 2, "category": "Basic Retrieval", "query": "What data sources does Northstar Insights support?"},
    {"id": 3, "category": "Basic Retrieval", "query": "How often do customer segments refresh?"},
    {"id": 4, "category": "Basic Retrieval", "query": "What encryption is used at rest?"},

    # Tool Use
    {"id": 5, "category": "Tool Use", "query": "Calculate the first-year cost for the Growth Plan on an annual contract for a nonprofit customer."},
    {"id": 6, "category": "Tool Use", "query": "Show all open support tickets for GreenMart."},
    {"id": 7, "category": "Tool Use", "query": "What is GreenMart's renewal risk?"},
    {"id": 8, "category": "Tool Use", "query": "Is a 5-day PTO request valid if submitted 7 business days in advance?"},

    # Multi-Hop RAG
    {"id": 9, "category": "Multi-Hop RAG", "query": "Why is UrbanBasket a good candidate for upgrading to Growth?"},
    {"id": 10, "category": "Multi-Hop RAG", "query": "Which internal projects are relevant to StyleHub?"},
    {"id": 11, "category": "Multi-Hop RAG", "query": "What issues should the customer success team discuss with GreenMart before renewal?"},
    {"id": 12, "category": "Multi-Hop RAG", "query": "Which customers are affected by integration issues?"},

    # Ambiguity / Robustness
    {"id": 13, "category": "Ambiguity / Robustness", "query": "Does the platform support Azure Synapse?"},
    {"id": 14, "category": "Ambiguity / Robustness", "query": "Can a customer with 4 months of sales history use forecasting?"},
    {"id": 15, "category": "Ambiguity / Robustness", "query": "Can nonprofit annual discounts be combined?"},
    {"id": 16, "category": "Ambiguity / Robustness", "query": "Who owns the fix for false positive inventory alerts?"},

    # Structured Output
    {"id": 17, "category": "Structured Output", "query": "Return open tickets grouped by customer in JSON."},
    {"id": 18, "category": "Structured Output", "query": "Create a customer risk table with customer, plan, renewal date, open tickets, and risk level."},
    {"id": 19, "category": "Structured Output", "query": "List all target releases by date."},
    {"id": 20, "category": "Structured Output", "query": "Give me a sales prep brief for UrbanBasket with citations."},
]


def run_all_evaluations(handle_query, k: int = 8) -> list[dict]:
    """Run every evaluation question through the pipeline and collect results."""
    results = []

    for item in EVALUATION_QUESTIONS:
        print(
            f"\n[{item['id']}/{len(EVALUATION_QUESTIONS)}] ({item['category']}) {item['query']}",
            flush=True,
        )

        try:
            result = handle_query(item["query"], k=k)
            results.append({
                "id": item["id"],
                "category": item["category"],
                "query": item["query"],
                "route": result["route"],
                "tool_name": result.get("tool_name"),
                "tool_args": result.get("tool_args"),
                "tool_result": result.get("tool_result"),
                "answer": result["answer"],
                "sources": [
                    {"source": s["metadata"].get("source"), "section": s["metadata"].get("section")}
                    for s in result["sources"]
                ] if result.get("sources") else None,
                "error": None,
            })
        except Exception as e:
            print(f"  [error] {e}", flush=True)
            results.append({
                "id": item["id"],
                "category": item["category"],
                "query": item["query"],
                "route": "error",
                "tool_name": None,
                "tool_args": None,
                "tool_result": None,
                "answer": None,
                "sources": None,
                "error": str(e),
            })

    return results


def write_raw_json(results: list[dict]) -> None:
    payload = {
        "generated_at": datetime.now().isoformat(),
        "question_count": len(results),
        "results": results,
    }
    RAW_OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nRaw results written to {RAW_OUTPUT_PATH}", flush=True)


def print_summary(results: list[dict]) -> None:
    by_route = {}
    for r in results:
        by_route[r["route"]] = by_route.get(r["route"], 0) + 1

    errors = sum(1 for r in results if r["error"])

    print("\n" + "=" * 50)
    print("EVALUATION SUMMARY")
    print("=" * 50)
    print(f"Total questions: {len(results)}")
    for route, count in sorted(by_route.items()):
        print(f"  {route}: {count}")
    print(f"Errors: {errors}")
    print("=" * 50)


if __name__ == "__main__":
    print("Starting evaluation runner...", flush=True)
    print("Loading pipeline (this may take a moment)...", flush=True)
    from main import build_index, handle_query

    print("Building index...", flush=True)
    build_index()

    k = 8

    print(f"\nRunning {len(EVALUATION_QUESTIONS)} evaluation questions ...", flush=True)
    results = run_all_evaluations(handle_query, k=k)

    write_raw_json(results)
    print_summary(results)
