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

These responses were then carried over to the evaluation markdown file (`evaluation_results.md`) where grading was done by hand after the automated run, comparing each answer against the the source documents directly. Each question was then given a correctness value of 'Correct', 'Partially Correct', or 'Incorrect'. Two genuine failures were found this way — see Known Limitations — with the root cause and proposed fix documented below.

This automated-evaluation approach was chosen over manually running and transcribing
each query individually to make the evaluation reproducible (anyone can re-run
`run_evaluation.py` and get the same structured comparison).

---

## Known Limitations + Potential Improvements

**Tool orchestration is regex-based and can misroute compound or table-style
requests.** The keyword-pattern router works reliably for single-entity, single-intent
queries (e.g. "What is GreenMart's renewal risk?") but struggles with requests that
need multiple tool calls or don't cleanly match one tool's pattern set. Concretely,
"Create a customer risk table with customer, plan, renewal date, open tickets, and
risk level" (evaluation question #18 / #24) was misrouted to `lookup_tickets` with
placeholder schema-type strings as arguments (the argument-extraction LLM echoed back
literal type names like `"string"` instead of leaving unmentioned fields empty),
producing an incorrect answer. A more robust fix would be a dedicated structured-output
handler that recognizes table/multi-customer requests and either calls
`classify_renewal_risk` per customer or routes through an LLM-driven planning step
capable of multi-tool calls, rather than a single regex-matched dispatch.

**Grounding is not airtight against plausible-sounding unsupported inferences.** When
asked whether the platform supports Azure Synapse (evaluation question #13/#19), the
model correctly identified that Azure Synapse isn't in the documented data source
list, but it added an unsupported claim that "BigQuery can be used to connect
to Azure Synapse" — a plausible-sounding inference not present in any retrieved
context. The system prompt instructs the model to answer only from context, but this
shows that instruction alone doesn't fully prevent a small local model from adding
adjacent claims it considers reasonable. A stronger guardrail (e.g. explicit
instruction to flag any claim not directly traceable to a cited chunk, or a
post-generation verification pass) would reduce this risk.

**No chunk-length guard.** Markdown sections are chunked as whole `##` blocks with no
sub-splitting. If a section significantly exceeded the embedding model's input limit,
it would be silently truncated. The current dataset's sections are short enough that
this hasn't been observed, but it's not actively guarded against.

**No retrieval score/distance filtering.** `retrieve()` always returns the top-`k`
chunks regardless of similarity score, which means low-relevance chunks can be
included in context on borderline queries, slightly increasing noise.

**Index rebuilds on every run.** ChromaDB uses an in-memory client with no
persistence, so the full corpus is re-embedded and re-indexed each time `main.py` or
`run_evaluation.py` starts. Fine for this corpus size; would not scale to a larger
production knowledge base without a persistent vector store.