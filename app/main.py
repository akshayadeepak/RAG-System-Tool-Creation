"""
Orchestration layer for the Northstar Insights RAG assistant.

Routing strategy:
  1. Check query against keyword/intent patterns to detect tool calls.
  2. If a tool is matched, extract arguments via a lightweight LLM call,
     dispatch the tool, then format the result back through the LLM.
  3. If no tool matches, fall through to the RAG pipeline.

This keeps tool dispatch deterministic while still allowing natural-language
argument extraction for ambiguous inputs.
"""

import json
import re
import sys
from typing import Optional

import httpx

from rag import ask, build_index, retrieve, OLLAMA_BASE_URL, OLLAMA_MODEL
from tools import dispatch_tool, TOOL_DEFINITIONS
from prompts import build_extraction_messages, build_format_messages

# Match queries to tools using keyword patterns
TOOL_PATTERNS: list[dict] = [
    {
        "tool": "calculate_pricing",
        "patterns": [
            r"\bpric(e|ing|ed)\b",
            r"\bcost\b",
            r"\bfirst.year\b",
            r"\bmonthly.*(fee|price|cost)\b",
            r"\bimplementation fee\b",
            r"\bplan\b.*\b(annual|monthly|nonprofit|discount)\b",
            r"\b(starter|growth|enterprise)\b.*\b(plan|cost|price)\b",
            r"\bupgrad(e|ing)\b.*\b(cost|price|fee)\b",
            r"\bdiscount\b",
            r"\bannual contract\b",
        ],
    },
    {
        "tool": "lookup_tickets",
        "patterns": [
            r"\bticket(s)?\b",
            r"\bopen issue(s)?\b",
            r"\bsupport (issue|case|request)(s)?\b",
            r"\b(open|resolved|in progress).*(issue|ticket|problem)\b",
            r"\bT-\d{4}\b",
        ],
    },
    {
        "tool": "classify_renewal_risk",
        "patterns": [
            r"\brenewal risk\b",
            r"\bchurn risk\b",
            r"\baccount health\b",
            r"\brisk.*(renew|churn)\b",
            r"\b(at risk|high risk|medium risk|low risk)\b",
        ],
    },
    {
        "tool": "find_relevant_projects",
        "patterns": [
            r"\bproject(s)?\b.*\brelevant\b",
            r"\brelevant.*\bproject(s)?\b",
            r"\binternal project(s)?\b",
            r"\bfix.*(coming|planned|scheduled|release)\b",
            r"\brelease date\b",
            r"\btarget release\b",
            r"\bwhen.*(fix|patch|update)\b",
            r"\bwhich project\b",
            r"\bproject.*stylehub\b",
            r"\bproject.*greenmart\b",
            r"\bproject.*urbanbasket\b",
        ],
    },
    {
        "tool": "check_pto_eligibility",
        "patterns": [
            r"\bleave request\b",
            r"\bvacation request\b",
            r"\btime off request\b",
            r"\bpto request\b",
            r"\bpto.*(valid|eligible|qualify|approve)\b",
            r"\b(eligible|qualify|approve).*(pto|leave|vacation)\b",
            r"\badvance notice\b.*\b(pto|leave|vacation|days)\b",
            r"\bdays? in advance\b",
        ],
    },
]


def detect_tool(query: str) -> Optional[str]:
    """Return the first tool name whose patterns match the query, or None."""
    q = query.lower()
    for entry in TOOL_PATTERNS:
        for pattern in entry["patterns"]:
            if re.search(pattern, q):
                return entry["tool"]
    return None


# ---------------------------------------------------------------------------
# Tool argument extraction
# ---------------------------------------------------------------------------

def extract_tool_args(query: str, tool_name: str) -> dict:
    """Ask the LLM to extract structured arguments for the given tool from the query."""
    tool_def = next((t for t in TOOL_DEFINITIONS if t["name"] == tool_name), None)
    if not tool_def:
        return {}

    messages = build_extraction_messages(query, tool_name, tool_def["parameters"])

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.0, "num_ctx": 2048},
    }

    try:
        response = httpx.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=httpx.Timeout(30.0, read=60.0),
        )
        response.raise_for_status()
        raw = response.json()["message"]["content"].strip()

        # Strip markdown fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        return json.loads(raw)
    except Exception as e:
        print(f"[warn] Argument extraction failed: {e}", flush=True)
        return {}


# ---------------------------------------------------------------------------
# Tool result formatting
# ---------------------------------------------------------------------------

def format_tool_result(query: str, tool_name: str, result: dict) -> str:
    """Ask the LLM to format a tool result into a natural-language response."""
    messages = build_format_messages(query, tool_name, result)

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": True,
        "options": {"temperature": 0.1, "num_ctx": 2048},
    }

    parts = []
    try:
        with httpx.stream(
            "POST",
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=httpx.Timeout(30.0, read=None),
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                chunk = json.loads(line)
                token = chunk.get("message", {}).get("content", "")
                if token:
                    parts.append(token)
                    print(token, end="", flush=True)
                if chunk.get("done"):
                    break
        if parts:
            print()
    except Exception as e:
        print(f"[error] Formatting failed: {e}", flush=True)
        return json.dumps(result, indent=2)

    return "".join(parts)


# ---------------------------------------------------------------------------
# Main query handler
# ---------------------------------------------------------------------------

def handle_query(query: str, k: int = 8, verbose: bool = False) -> dict:
    """
    Route a query to a tool or the RAG pipeline and return a structured result.

    Returns:
        {
            "query": str,
            "route": "tool" | "rag" | "rag_fallback",
            "tool_name": str | None,
            "tool_args": dict | None,
            "tool_result": dict | None,
            "answer": str,
            "sources": list | None,
        }
    """
    tool_name = detect_tool(query)

    if tool_name:
        print(f"[router] Detected tool: {tool_name}", flush=True)

        # Extract arguments
        args = extract_tool_args(query, tool_name)
        print(f"[router] Extracted args: {args}", flush=True)

        # Dispatch tool
        try:
            tool_result = dispatch_tool(tool_name, args)
        except Exception as e:
            print(f"[error] Tool dispatch failed: {e}", flush=True)
            # Fall back to RAG
            print("[router] Falling back to RAG", flush=True)
            rag_result = ask(query, k=k)
            return {
                "query": query,
                "route": "rag_fallback",
                "tool_name": tool_name,
                "tool_args": args,
                "tool_result": None,
                "answer": rag_result["answer"],
                "sources": rag_result["sources"],
            }

        # Format result into natural language
        print("[router] Formatting tool result...", flush=True)
        answer = format_tool_result(query, tool_name, tool_result)

        return {
            "query": query,
            "route": "tool",
            "tool_name": tool_name,
            "tool_args": args,
            "tool_result": tool_result,
            "answer": answer,
            "sources": None,
        }

    else:
        print("[router] No tool matched — routing to RAG", flush=True)
        rag_result = ask(query, k=k)
        return {
            "query": query,
            "route": "rag",
            "tool_name": None,
            "tool_args": None,
            "tool_result": None,
            "answer": rag_result["answer"],
            "sources": rag_result["sources"],
        }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def print_result(result: dict) -> None:
    print("\n" + "=" * 60)
    print(f"Query : {result['query']}")
    print(f"Route : {result['route']}")
    if result.get("tool_name"):
        print(f"Tool  : {result['tool_name']}")
    if result.get("tool_args"):
        print(f"Args  : {json.dumps(result['tool_args'])}")
    print("-" * 60)
    if result["route"] != "tool":
        print(result["answer"])
    if result.get("sources"):
        print("\nRetrieved chunks:")
        for i, s in enumerate(result["sources"], 1):
            meta = s["metadata"]
            print(f"  {i}. [{meta['source']} | {meta['section']}]")
    print("=" * 60)


DEMO_QUERIES = [
    # Tool queries
    "Calculate the first-year cost for the Growth Plan on an annual contract for a nonprofit customer.",
    "Show all open support tickets for GreenMart.",
    "What is GreenMart's renewal risk?",
    "Is a 5-day PTO request valid if submitted 7 business days in advance?",
    "Which internal projects are relevant to StyleHub?",
    # RAG queries
    "How many PTO days do full-time employees receive?",
    "What data sources does Northstar Insights support?",
    "Why is UrbanBasket a good candidate for upgrading to Growth?",
    "Does the platform support Azure Synapse?",
    "What issues should the customer success team discuss with GreenMart before renewal?",
]


if __name__ == "__main__":
    print("Building index...", flush=True)
    build_index()

    # If a query is passed as CLI arg, run just that
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        result = handle_query(query, verbose=True)
        print_result(result)
        sys.exit(0)

    print(f"\nRunning {len(DEMO_QUERIES)} demo queries...\n", flush=True)
    for query in DEMO_QUERIES:
        result = handle_query(query)
        print_result(result)