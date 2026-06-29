import asyncio
import json
from collections.abc import AsyncIterator

from app.core.errors import AppError
from app.schemas.agent_runs import AgentRunCreate, AgentRunRead, agent_run_stub


class AgentRunService:
    def __init__(self) -> None:
        self._runs: dict[str, AgentRunRead] = {}
        self._request_ids: set[tuple[str, str]] = set()

    async def create_run(self, payload: AgentRunCreate) -> AgentRunRead:
        idempotency_key = (payload.topic_profile_id, payload.request_id)
        if idempotency_key in self._request_ids:
            raise AppError(
                "CONFLICT",
                "request_id already exists for this topic profile.",
                status_code=409,
            )

        run = agent_run_stub(payload)
        self._runs[run.id] = run
        self._request_ids.add(idempotency_key)
        return run

    async def get_run(self, run_id: str) -> AgentRunRead:
        if run_id not in self._runs:
            raise AppError("RESOURCE_NOT_FOUND", "Agent run not found.", status_code=404)
        return self._runs[run_id]

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


_agent_run_service = AgentRunService()


def get_agent_run_service() -> AgentRunService:
    return _agent_run_service
