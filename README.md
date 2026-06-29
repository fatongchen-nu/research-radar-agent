# Research Radar Agent

Autonomous research monitoring and evidence intelligence system.

This project is the MVP version of the second resume project from `backend-agent-project-resume-pack.md`: a Yuxi-style async Agent platform plus a DocETL-style ingestion pipeline for monitoring new papers, extracting claims, and answering research questions with citations.

## MVP Scope

- Create topic profiles for research ideas.
- Fetch paper metadata from arXiv and Semantic Scholar-style sources.
- Deduplicate papers by DOI, source id, arXiv id, and normalized title.
- Extract structured evidence claims from abstracts or PDF text.
- Store papers, chunks, evidence claims, ingestion runs, agent runs, feedback, and daily digests.
- Answer questions through async Agent runs with SSE event streaming.
- Evaluate answer quality with citation accuracy, stance accuracy, paper hit rate, and claim extraction metrics.

## First Architecture

```text
Daily Scheduler
  -> Source Fetchers
  -> Paper Dedup / Metadata Enrichment
  -> Evidence Extraction Pipeline
  -> Paper / Claim / Evidence Tables
  -> Keyword + Vector Retrieval
  -> Agent Run Service
  -> SSE Answer Stream / Daily Digest / Feedback
```

## Project Layout

```text
app/
  api/v1/routes/       REST API endpoints
  core/                settings, errors, shared infrastructure
  db/                  SQLAlchemy session and ORM models
  etl/                 fetch, dedup, extract, and pipeline steps
  repositories/        memory and Postgres persistence adapters
  schemas/             Pydantic request/response models
  services/            business logic
  workers/             scheduler and background jobs
migrations/            SQL schema bootstrap
tests/                 smoke tests
docs/                  architecture notes
```

## Quick Start

```bash
cp .env.example .env
uv sync --all-extras --dev
uv run uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs`.

For a zero-database smoke test, set:

```bash
REPOSITORY_BACKEND=memory
```

For the real backend path, keep:

```bash
REPOSITORY_BACKEND=postgres
```

## Docker Services

```bash
docker compose up -d postgres redis
```

The first version uses Postgres plus Redis. Add pgvector or Qdrant once the ingestion and Agent run flow is stable.

## Initial API Surface

- `GET /api/v1/health`
- `POST /api/v1/topics`
- `GET /api/v1/topics`
- `POST /api/v1/topics/{topic_id}/ingestion-runs`
- `GET /api/v1/ingestion-runs/{run_id}`
- `POST /api/v1/agent/runs`
- `GET /api/v1/agent/runs/{run_id}`
- `GET /api/v1/agent/runs/{run_id}/events`
- `GET /api/v1/topics/{topic_id}/digest/today`

## Next Build Steps

1. Persist fetched papers, chunks, and extracted claims through repository classes.
2. Add claim extraction with structured LLM output and validation retry.
3. Add keyword retrieval first, then pgvector or Qdrant retrieval.
4. Persist Agent run events to Redis stream and replay them through SSE.
5. Connect the scheduler to topic profiles and ingestion runs.
6. Expand the evaluation set from sample records to 30 gold records.
