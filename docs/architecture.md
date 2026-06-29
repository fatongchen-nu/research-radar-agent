# Architecture Notes

## Product Loop

1. User creates a topic profile for a research idea.
2. Scheduler fetches new papers for the topic.
3. Ingestion pipeline deduplicates papers and filters by relevance.
4. Evidence extraction produces claim, method, finding, stance, quote, and confidence records.
5. Retrieval returns paper, chunk, and claim references.
6. Agent run answers questions with supporting evidence, contradicting evidence, limitations, and citations.
7. Feedback and evaluation records improve future extraction and retrieval.

## MVP Boundaries

- Keep online Agent runtime separate from offline ingestion.
- Use Postgres as the system of record.
- Start with keyword retrieval and add pgvector after the paper/evidence schema stabilizes.
- Use Redis streams for Agent run events once the in-memory SSE prototype is stable.
- Prefer local sample papers for demo repeatability, then add live APIs.

## Resume Signals

- Async Agent run lifecycle with idempotency, cancellation, retry, and SSE.
- DocETL-style batch pipeline with checkpointable fetch, dedup, extraction, and indexing steps.
- Citation-grounded RAG over paper, chunk, and evidence claim entities.
- Evaluation loop for paper hit rate, citation accuracy, stance accuracy, and claim extraction F1.
