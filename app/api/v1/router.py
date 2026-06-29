from fastapi import APIRouter

from app.api.v1.routes import agent_runs, demo, digests, health, ingestion, topics

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
api_router.include_router(topics.router, prefix="/topics", tags=["topics"])
api_router.include_router(ingestion.router, tags=["ingestion"])
api_router.include_router(agent_runs.router, prefix="/agent/runs", tags=["agent-runs"])
api_router.include_router(digests.router, tags=["digests"])
