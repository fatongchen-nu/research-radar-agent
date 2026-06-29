from fastapi.testclient import TestClient

from app.main import create_app


def test_health() -> None:
    client = TestClient(create_app())
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_topic() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/topics",
        json={
            "name": "AI adoption and analyst forecasts",
            "research_idea": "AI adoption may improve analyst forecast accuracy.",
            "keywords": ["AI adoption", "forecast accuracy"],
        },
    )

    assert response.status_code == 201
    assert response.json()["name"] == "AI adoption and analyst forecasts"


def test_demo_sample_ingestion() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/api/v1/demo/sample-ingestion",
        json={
            "name": "AI adoption and analyst forecasts",
            "research_idea": "AI adoption may improve analyst forecast accuracy.",
            "keywords": ["AI adoption", "forecast accuracy"],
            "source_limit": 20,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["topic"]["name"] == "AI adoption and analyst forecasts"
    assert data["ingestion_run"]["status"] == "completed"
    assert data["ingestion_run"]["extracted_claims"] >= 1


def test_agent_run_returns_citation_grounded_answer_after_demo_ingestion() -> None:
    client = TestClient(create_app())
    demo_response = client.post(
        "/api/v1/demo/sample-ingestion",
        json={
            "name": "AI adoption and analyst forecasts",
            "research_idea": "AI adoption may improve analyst forecast accuracy.",
            "keywords": ["AI adoption", "forecast accuracy"],
            "source_limit": 20,
        },
    )
    topic_id = demo_response.json()["topic"]["id"]

    run_response = client.post(
        "/api/v1/agent/runs",
        json={
            "topic_profile_id": topic_id,
            "request_id": "demo-question-agent-answer",
            "question": "Does AI adoption improve analyst forecast accuracy?",
        },
    )

    assert run_response.status_code == 202
    run = run_response.json()
    assert run["status"] == "completed"
    assert "Question:" in run["answer"]
    assert run["citations"]
    assert run["token_usage"]["retrieved_claims"] >= 1


def test_agent_run_events_include_answer_payload() -> None:
    client = TestClient(create_app())
    demo_response = client.post(
        "/api/v1/demo/sample-ingestion",
        json={
            "name": "AI adoption and analyst forecasts",
            "research_idea": "AI adoption may improve analyst forecast accuracy.",
            "keywords": ["AI adoption", "forecast accuracy"],
            "source_limit": 20,
        },
    )
    topic_id = demo_response.json()["topic"]["id"]
    run_response = client.post(
        "/api/v1/agent/runs",
        json={
            "topic_profile_id": topic_id,
            "request_id": "demo-question-agent-events",
            "question": "Does AI adoption improve analyst forecast accuracy?",
        },
    )
    run_id = run_response.json()["id"]

    events_response = client.get(f"/api/v1/agent/runs/{run_id}/events")

    assert events_response.status_code == 200
    assert "answer.completed" in events_response.text
    assert "run.completed" in events_response.text
