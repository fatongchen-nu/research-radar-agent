import asyncio
import json
from collections.abc import AsyncIterator

from fastapi import Depends

from app.core.errors import AppError
from app.repositories.dependencies import get_agent_run_repository
from app.repositories.run_repository import AgentRunRepository
from app.schemas.agent_runs import AgentRunCreate, AgentRunRead


class AgentRunService:
    def __init__(self, repository: AgentRunRepository) -> None:
        self.repository = repository

    async def create_run(self, payload: AgentRunCreate) -> AgentRunRead:
        existing = await self.repository.find_by_request_id(
            payload.topic_profile_id,
            payload.request_id,
        )
        if existing is not None:
            raise AppError(
                "CONFLICT",
                "request_id already exists for this topic profile.",
                status_code=409,
            )

        return await self.repository.create(payload)

    async def get_run(self, run_id: str) -> AgentRunRead:
        run = await self.repository.get(run_id)
        if run is None:
            raise AppError("RESOURCE_NOT_FOUND", "Agent run not found.", status_code=404)
        return run

    async def stream_events(self, run_id: str) -> AsyncIterator[str]:
        run = await self.get_run(run_id)
        events = [
            {"type": "run.queued", "run_id": run.id},
            {"type": "retrieval.started", "message": "Searching paper and evidence indexes."},
            {"type": "answer.partial", "message": "Citation-grounded answer generation pending."},
            {"type": "run.completed", "status": run.status},
        ]
        for event in events:
            yield f"data: {json.dumps(event)}\n\n"
            await asyncio.sleep(0.05)


def get_agent_run_service(
    repository: AgentRunRepository = Depends(get_agent_run_repository),
) -> AgentRunService:
    return AgentRunService(repository)
