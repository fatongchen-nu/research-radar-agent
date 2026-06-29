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
