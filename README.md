# Northstar RAG Assistant

A GenAI assistant for an internal enterprise knowledge environment. Answers questions
about HR policy, product documentation, pricing, support tickets, sales notes, and
internal projects — combining retrieval-augmented generation with deterministic tool
calls for operational queries (pricing calculations, ticket lookups, renewal risk,
PTO eligibility).

See [`design_decisions.md`](./design_decisions.md) for architecture, design decisions, and
known limitations.

---

## Setup

### 1. Install Ollama

Download and install from [ollama.com](https://ollama.com), or via terminal:

```bash
# macOS
brew install ollama

# or download directly from https://ollama.com
```

Start the Ollama server (if it doesn't start automatically):

```bash
ollama serve
```

### 2. Pull the model

This project uses `llama3.2:3b` by default — a small, fast local model.

```bash
ollama pull llama3.2:3b
```

### 3. Set up the Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate 

pip install -r requirements.txt
```

### 4. Run the assistant

Run the full demo query set:

```bash
python app/main.py
```

Run a single query:

```bash
python app/main.py "Calculate the first-year cost for the Growth Plan on an annual contract for a nonprofit customer."
```

Run the full automated evaluation (all 20 assignment questions):

```bash
python app/run_evaluation.py
```

This writes `results/evaluation_raw.json`.

You can override the embedding model or Ollama settings via environment variables:

```bash
export OLLAMA_BASE_URL="http://localhost:11434"   # default
export OLLAMA_MODEL="llama3.2:3b"                 # default
```

**Note:** The very first run can take a while (~10-15 mins) for ChromaDB to load. However subsequent runs will run much faster.

---

## Project Structure

```
app/
  results/
    evaluation_raw.json
  main.py            # Orchestration: routes queries to tools or RAG
  rag.py             # Document loading, chunking, indexing, retrieval, generation
  tools.py           # Pricing calculator, ticket lookup, renewal risk, project finder, PTO checker
  prompts.py          # Centralized prompt templates
  run_evaluation.py   # Automated evaluation runner
data/
  hr_policy.md
  product_docs.md
  pricing_rules.md
  support_tickets.csv
  sales_notes.md
  project_updates.md
examples/
  demo_queries.md       # 10 example queries with outputs
  evaluation_results.md # All evaluation questions, graded for correctness
design_decisions.md
requirements.txt
README.md
```
