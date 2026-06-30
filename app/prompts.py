"""
Prompt templates for the Northstar Insights RAG assistant.
"""

# RAG generation prompt
RAG_SYSTEM = """You are an internal assistant for Northstar Insights employees.
Answer the user's question using ONLY the context excerpts below.
The context is authorized internal company data — summarize it directly when asked.
If the question asks "why", "which", "compare", "recommend", or "evaluate", combine evidence from every relevant retrieved document into a single answer.
End your answer with a short "Sources:" line listing the file and section you used.
If the context does not contain the answer, say: "I could not find this in the knowledge base."
"""


def build_rag_messages(query: str, chunks: list[dict]) -> list[dict]:
    """
    Build the message list for a RAG generation call.

    Args:
        query:  The user's question.
        chunks: Retrieved context chunks from the vector store.

    Returns:
        A list of messages in Ollama/OpenAI chat format.
    """
    context = "\n\n---\n\n".join(
        f"Source: {chunk['metadata']['source']} | {chunk['metadata']['section']}\n"
        f"{chunk['text']}"
        for chunk in chunks
    )

    user_content = f"""Context: {context}

    Question: {query}"""

    return [
        {"role": "system", "content": RAG_SYSTEM},
        {"role": "user", "content": user_content},
    ]


# Tool argument extraction prompt
EXTRACTION_SYSTEM = """You are an argument extractor for a tool-calling system.
Given a user query and a tool schema, extract the arguments needed to call the tool.
Return ONLY a valid JSON object with the argument names as keys.
Do not include keys for optional arguments that are not mentioned.
Do not include any explanation, preamble, or markdown formatting."""


def build_extraction_messages(query: str, tool_name: str, tool_schema: dict) -> list[dict]:
    """
    Build the message list for a tool argument extraction call.

    Args:
        query:       The user's natural language query.
        tool_name:   The name of the tool to extract arguments for.
        tool_schema: The tool's parameter schema (from TOOL_DEFINITIONS).

    Returns:
        A list of messages in Ollama/OpenAI chat format.
    """
    import json

    user_content = f"""Tool: {tool_name}
    Schema: {json.dumps(tool_schema, indent=2)}

    User query: {query}

    Extract the arguments as a JSON object."""

    return [
        {"role": "system", "content": EXTRACTION_SYSTEM},
        {"role": "user", "content": user_content},
    ]


# Tool result formatting prompt
FORMAT_SYSTEM = """You are an internal assistant for Northstar Insights employees.
You have just called a tool and received its structured result.
Summarize the result in clear, concise prose for the user.
Be specific — include all key numbers, dates, ticket IDs, and reasons from the result.
End with a short "Source: [tool name]" line.
Do not invent any information not present in the tool result."""


def build_format_messages(query: str, tool_name: str, tool_result: dict) -> list[dict]:
    """
    Build the message list for formatting a tool result into natural language.

    Args:
        query:       The original user query.
        tool_name:   The name of the tool that was called.
        tool_result: The structured result returned by the tool.

    Returns:
        A list of messages in Ollama/OpenAI chat format.
    """
    import json

    user_content = f"""User query: {query}

    Tool called: {tool_name}

    Tool result: {json.dumps(tool_result, indent=2)}

    Write a clear, complete answer to the user's query based on this result."""

    return [
        {"role": "system", "content": FORMAT_SYSTEM},
        {"role": "user", "content": user_content},
    ]