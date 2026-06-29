# Local Setup Checklist

## What You Need To Do

1. Install `uv` if it is not installed.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Create your local env file.

```bash
cp .env.example .env
```

3. Start in memory mode first.

```bash
REPOSITORY_BACKEND=memory
PAPER_FETCHER=sample
uv sync --all-extras --dev
uv run uvicorn app.main:app --reload
```

4. Open the API docs.

```text
http://localhost:8000/docs
```

5. For the least confusing first run, use the one-click demo endpoint:

```text
POST /api/v1/demo/sample-ingestion
```

Body:

```json
{
  "name": "AI adoption and analyst forecasts",
  "research_idea": "AI adoption may improve analyst forecast accuracy.",
  "keywords": ["AI adoption", "forecast accuracy"],
  "source_limit": 20
}
```

It creates a topic and triggers ingestion in the same request.

After that, call:

```text
POST /api/v1/agent/runs
```

Use the topic id returned by the demo endpoint:

```json
{
  "topic_profile_id": "paste-topic-id-here",
  "request_id": "demo-question-001",
  "question": "Does AI adoption improve analyst forecast accuracy?"
}
```

The response should return `status: "completed"`, a citation-grounded `answer`, and at least one citation.

## Manual Topic Flow

Create a topic profile with keywords such as:

```json
{
  "name": "AI adoption and analyst forecasts",
  "research_idea": "AI adoption may improve analyst forecast accuracy.",
  "keywords": ["AI adoption", "forecast accuracy"]
}
```

Then trigger ingestion.

```text
POST /api/v1/topics/{topic_id}/ingestion-runs
```

With `PAPER_FETCHER=sample`, this uses local sample papers and should complete without API keys.

## When You Want Postgres

1. Start Docker services.

```bash
docker compose up -d postgres redis
```

2. Update `.env`.

```bash
REPOSITORY_BACKEND=postgres
PAPER_FETCHER=sample
```

3. Restart the API.

```bash
uv run uvicorn app.main:app --reload
```

## When You Want Live arXiv

Update `.env`.

```bash
PAPER_FETCHER=arxiv
```

The arXiv fetcher falls back to local sample data if the live request fails.

## Not Needed Yet

- OpenAI API key is not required until structured LLM extraction is implemented.
- Semantic Scholar key is not required until the second live source is added.
- Redis is not required until Agent run event streaming is moved from placeholder SSE to Redis streams.
