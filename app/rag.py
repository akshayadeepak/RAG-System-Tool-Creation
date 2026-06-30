"""RAG pipeline: chunk documents, index in ChromaDB, retrieve context, answer via Ollama."""

import json
import csv
import os
import re
from pathlib import Path

import chromadb
import httpx
from chromadb.errors import NotFoundError
from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import ONNXMiniLM_L6_V2

from prompts import build_rag_messages as build_messages

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
COLLECTION_NAME = "knowledge_base"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

_collection = None


def load_markdown_sections(path: Path) -> list[dict]:
    """Split a markdown file into chunks at each ## heading.

    Returns a list of dicts with keys: text, source, section, type.
    Content before the first ## becomes its own chunk titled from the # heading.
    """
    content = path.read_text(encoding="utf-8")
    chunks = []

    parts = re.split(r"^(## .+)$", content, flags=re.MULTILINE)

    preamble = parts[0].strip()
    if preamble:
        title_match = re.search(r"^# (.+)$", preamble, flags=re.MULTILINE)
        section = title_match.group(1).strip() if title_match else "Introduction"
        chunks.append(
            {
                "text": preamble,
                "source": path.name,
                "section": section,
                "type": "markdown",
            }
        )

    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ""
        section = heading.lstrip("#").strip()
        text = f"{heading}\n\n{body}".strip() if body else heading
        chunks.append(
            {
                "text": text,
                "source": path.name,
                "section": section,
                "type": "markdown",
            }
        )

    return chunks


def load_csv_rows(path: Path) -> list[dict]:
    """Convert each CSV row into a searchable text chunk with ticket metadata."""
    docs = []
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            text = (
                f"Ticket {row['ticket_id']} from {row['customer']} ({row['date']}): "
                f"[{row['priority']}] {row['category']} - {row['summary']} "
                f"Status: {row['status']}"
            )
            docs.append(
                {
                    "text": text,
                    "source": path.name,
                    "section": row["ticket_id"],
                    "type": "csv",
                    "ticket_id": row["ticket_id"],
                    "customer": row["customer"],
                    "priority": row["priority"],
                    "category": row["category"],
                }
            )
    return docs


def load_documents() -> list[dict]:
    """Load and chunk all .md and .csv files from the data directory."""
    docs = []
    for path in sorted(DATA_DIR.iterdir()):
        if path.suffix == ".md":
            docs.extend(load_markdown_sections(path))
        elif path.suffix == ".csv":
            docs.extend(load_csv_rows(path))
    return docs


def build_index():
    """Embed all document chunks and store them in a fresh ChromaDB collection.

    Rebuilds the collection on each call. Sets the module-level _collection cache.
    Returns the collection and the list of loaded document chunks.
    """
    global _collection

    print("Loading documents...", flush=True)
    documents = load_documents()
    print(f"  Found {len(documents)} chunks", flush=True)

    print("Loading embedding model (ONNX, no PyTorch)...", flush=True)
    embedding_fn = ONNXMiniLM_L6_V2()
    print("  Model ready", flush=True)

    print("Connecting to ChromaDB...", flush=True)
    client = chromadb.Client()

    try:
        client.delete_collection(COLLECTION_NAME)
    except NotFoundError:
        pass

    collection = client.create_collection(
        COLLECTION_NAME,
        embedding_function=embedding_fn,
    )

    print("Indexing chunks...", flush=True)
    texts = [doc["text"] for doc in documents]
    collection.add(
        ids=[str(i) for i in range(len(documents))],
        documents=texts,
        metadatas=[{k: v for k, v in doc.items() if k != "text"} for doc in documents],
    )
    print("  Indexing complete", flush=True)

    _collection = collection
    return collection, documents


def get_index():
    """Return the ChromaDB collection, building the index first if needed."""
    if _collection is None:
        build_index()
    return _collection


def retrieve(query: str, k: int = 5) -> list[dict]:
    """Return the top-k most similar chunks for a query.

    Each result is a dict with "text" and "metadata" (source, section, type, etc.).
    """
    collection = get_index()

    results = collection.query(
        query_texts=[query],
        n_results=k,
        include=["documents", "metadatas"],
    )

    return [
        {"text": doc, "metadata": meta}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]


def ask_ollama(
    messages: list[dict],
    model: str = OLLAMA_MODEL,
    base_url: str = OLLAMA_BASE_URL,
    stream: bool = True,
) -> str:
    """Send messages to the Ollama chat API and return the model's reply.

    Streams tokens to stdout by default. Raises RuntimeError on connection,
    missing model, or timeout errors.
    """
    payload = {
        "model": model,
        "messages": messages,
        "stream": stream,
        "options": {"num_ctx": 4096, "temperature": 0.1},
    }

    try:
        if stream:
            parts = []
            with httpx.stream(
                "POST",
                f"{base_url}/api/chat",
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
            return "".join(parts)

        response = httpx.post(
            f"{base_url}/api/chat",
            json=payload,
            timeout=httpx.Timeout(30.0, read=600.0),
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    except httpx.ConnectError as exc:
        raise RuntimeError(
            "Could not connect to Ollama. Install it from https://ollama.com, "
            "start the server, then run: ollama pull llama3.2:3b"
        ) from exc
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise RuntimeError(
                f"Model '{model}' not found. Run: ollama pull {model}"
            ) from exc
        raise
    except httpx.ReadTimeout as exc:
        raise RuntimeError(
            f"Ollama timed out waiting for '{model}'. "
            "Try: ollama pull llama3.2:3b"
        ) from exc


def ask(query: str, k: int = 5, model: str = OLLAMA_MODEL) -> dict:
    """Run the full RAG pipeline: retrieve context, prompt Ollama, return the answer.

    Returns a dict with keys: query, answer, sources (the retrieved chunks).
    """
    chunks = retrieve(query, k=k)
    messages = build_messages(query, chunks)
    answer = ask_ollama(messages, model=model)

    return {
        "query": query,
        "answer": answer,
        "sources": chunks,
    }


if __name__ == "__main__":
    print("Starting RAG pipeline...", flush=True)
    build_index()

    query = "Which internal projects are relevant to StyleHub?"
    print(f"\nQuery: {query}", flush=True)

    print("\nRetrieved context:", flush=True)
    for i, result in enumerate(retrieve(query), 1):
        meta = result["metadata"]
        print(f"  {i}. [{meta['source']} | {meta['section']}]", flush=True)

    print(f"\nAsking Ollama ({OLLAMA_MODEL})...\n", flush=True)
    result = ask(query)

    print("\n--- Answer ---", flush=True)
    if not result["answer"]:
        print("(see streamed output above)", flush=True)
    else:
        print(result["answer"], flush=True)