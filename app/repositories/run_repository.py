from typing import Protocol

from app.schemas.agent_runs import AgentRunCreate, AgentRunRead
from app.schemas.ingestion import IngestionRunRead


class AgentRunRepository(Protocol):
    async def create(self, payload: AgentRunCreate) -> AgentRunRead:
        ...

    async def get(self, run_id: str) -> AgentRunRead | None:
        ...

    async def find_by_request_id(self, topic_profile_id: str, request_id: str) -> AgentRunRead | None:
        ...


class IngestionRunRepository(Protocol):
    async def create(self, topic_id: str) -> IngestionRunRead:
        ...

    async def get(self, run_id: str) -> IngestionRunRead | None:
        ...
