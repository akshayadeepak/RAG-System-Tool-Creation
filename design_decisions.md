# Design Note

## Architecture Overview

**RAG pipeline** — Markdown files are chunked by `##` heading (each section becomes a chunk, with the heading kept in the chunk text so the embedding captures both the topic and the content). CSV ticket rows become one chunk each, flattened into a readable sentence with key fields (status, priority, category) explicitly named so they're embeddable, not just stored as metadata. Embeddings use `ONNXMiniLM_L6_V2`. Chunks are indexed in an in-memory ChromaDB collection and retrieved via similarity search (default `k=8`). Retrieved chunks are assembled into a prompt instructing the model to answer only from context, cite sources, and explicitly say when an answer isn't in the knowledge base.

**Tool layer** — Five deterministic Python functions (`tools.py`), each with a Pydantic input schema for validation: pricing calculator, support ticket lookup, renewal risk classifier, project release finder, and PTO eligibility checker. Tools never touch the LLM or the vector store — they read structured data (hardcoded pricing constants, the tickets CSV, hardcoded project/renewal data) and return deterministic JSON.

**Orchestration** — `main.py` routes each query in two stages. First, a regex/keyword pattern match against the query decides whether it looks like a tool-call intent (e.g. "renewal risk", "ticket", "PTO request") or should fall through to RAG. If a tool is matched, an LLM call extracts structured arguments from the natural-language query against the tool's schema, the tool is dispatched, and a second LLM call formats the structured result into a natural-language answer. If tool dispatch fails for any reason, the system falls back to RAG rather than crashing. This handles cases where the regex matches a query that doesn't actually need a tool call, and the fallback to RAG prevents the system from returning a bad tool result when dispatch fails or doesn't apply.

**Prompts** — All system prompts and prompt-building functions live in `prompts.py`,
separate from the RAG and orchestration logic, so prompt changes don't require editing
pipeline code.

---

## Key Design Decisions

**Custom orchestration.** I chose custom orchestration for full visibility into the routing decision (regex match → argument extraction → tool dispatch → formatting), which made debugging and explaining failure modes straightforward, at the cost of a more brittle router than a framework's built-in function-calling would provide.

**ONNX embeddings over `sentence_transformers`.** `ONNXMiniLM_L6_V2` avoids a PyTorch
installation, which meaningfully reduced setup time and environment fragility, and has
a lighter dependency footprint and faster cold start — with no meaningful quality
tradeoff for a corpus this size.

**Hardcoded pricing/policy constants rather than RAG-retrieved.** The pricing
calculator and PTO checker treat pricing tiers, discount rates, and policy thresholds
as structured config, not retrieved knowledge. Tools are required to produce
deterministic outputs; retrieving these values from the vector store would introduce
retrieval uncertainty into what should be a guaranteed computation.

**Plain `csv` module over Pandas.** The ticket dataset is 8 rows. Pandas would be
correct but unnecessary overhead for this scale, and avoiding it keeps the dependency
footprint consistent with the ONNX choice above.

---

## Evaluation Approach

All 20 evaluation questions from the assignment brief were run through an automated evaluation script (`app/run_evaluation.py`) that calls the live pipeline end-to-end. The script captures, for every question: the routing decision (tool vs. RAG vs. RAG fallback), the tool name and extracted arguments where applicable, the full answer text, and the retrieved source chunks. Results are written to both a structured JSON file.

These responses were then carried over to the evaluation markdown file (`evaluation_results.md`) where grading was done by hand after the automated run, comparing each answer against the the source documents directly. Each question was then given a correctness value of 'Correct', 'Partially Correct', or 'Incorrect'. The automated evaluation identified four partially correct cases and one incorrect structured-output case. These were analyzed manually by comparing the generated responses against the source documents. The identified issues are discussed in the Known Limitations section together with potential improvements.

This automated-evaluation approach was chosen over manually running and transcribing
each query individually to make the evaluation reproducible (anyone can re-run
`run_evaluation.py` and get the same structured comparison).

---

## Known Limitations + Potential Improvements

**Tool orchestration is regex-based and can misroute compound or table-style
requests.** The regex-based router assumes a single tool invocation per query. Consequently, table-generation or multi-entity requests (evaluation question #18) may be routed to a tool that cannot satisfy the full request, resulting in incorrect structured output. A more robust fix would be a dedicated structured-output handler that recognizes table/multi-customer requests and either calls `classify_renewal_risk` per customer or routes through an LLM-driven planning step capable of multi-tool calls, rather than a single regex-matched dispatch.

**The generation step does not always fully synthesize all retrieved evidence.** During evaluation, two questions (#17 and #19) retrieved all of the information needed to answer correctly, but the LLM produced only partially complete answers by using only a subset of the retrieved context. The retrieval stage therefore succeeded, but the generation stage did not consistently integrate every relevant chunk into a comprehensive response. This is a limitation of the current single-pass generation pipeline. Although the relevant evidence is retrieved successfully, the model is not explicitly required to account for every retrieved chunk before producing an answer.

**No chunk-length guard.** Markdown sections are chunked as whole `##` blocks with no
sub-splitting. If a section significantly exceeded the embedding model's input limit,
it would be silently truncated. The current dataset's sections are short enough that
this hasn't been observed, but it's not actively guarded against.

**No retrieval score/distance filtering.** `retrieve()` always returns the top-`k`
chunks regardless of similarity score, which may introduce low-relevance context and provides no mechanism for prioritizing the most relevant evidence before generation.