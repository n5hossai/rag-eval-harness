# rag-eval-harness

Measuring what actually makes retrieval-augmented generation work — on U.S. federal
aviation regulations (14 CFR).

> **Status:** in progress. Pipeline and evaluation harness under construction;
> the results table below is the deliverable.

Most RAG projects stop at "it answers questions." This one starts there and asks the
harder question: *how do you know it's answering them correctly, and which of your
design choices actually moved the number?*

The corpus is Title 14 of the Code of Federal Regulations — the FAA rules governing
airworthiness, maintenance, and flight operations. Every section carries a canonical
citation (`14 CFR § 43.13`), which means retrieval quality can be measured against
ground truth rather than eyeballed.

## Planned experiments

| Configuration | Recall@5 | MRR | Context Precision | Faithfulness | Answer Relevancy |
|---|---|---|---|---|---|
| Dense (MiniLM) baseline | — | — | — | — | — |
| Dense (bge-large) | — | — | — | — | — |
| BM25 lexical only | — | — | — | — | — |
| Hybrid (RRF) | — | — | — | — | — |
| Hybrid + cross-encoder rerank | — | — | — | — | — |

## Getting started

```bash
python -m venv .venv && .venv/Scripts/activate   # or source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

The ingestion and query commands land as the pipeline comes together.

## License

MIT. Corpus text is U.S. Government work in the public domain.
