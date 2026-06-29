from typing import Protocol

from app.schemas.agent_runs import AgentRunCreate, AgentRunRead
from app.schemas.ingestion import IngestionRunRead


class AgentRunRepository(Protocol):
    async def create(self, payload: AgentRunCreate) -> AgentRunRead:
        ...

    async def get(self, run_id: str) -> AgentRunRead | None:
        ...

    async def find_by_request_id(
        self,
        topic_profile_id: str,
        request_id: str,
    ) -> AgentRunRead | None:
        ...

    async def mark_completed(
        self,
        run_id: str,
        answer: str,
        citations: list[dict],
        token_usage: dict | None = None,
    ) -> AgentRunRead | None:
        ...


class IngestionRunRepository(Protocol):
    async def create(self, topic_id: str) -> IngestionRunRead:
        ...

    async def get(self, run_id: str) -> IngestionRunRead | None:
        ...

    async def mark_completed(
        self,
        run_id: str,
        new_papers: int,
        extracted_claims: int,
    ) -> IngestionRunRead | None:
        ...

    async def mark_failed(self, run_id: str, errors: list[dict]) -> IngestionRunRead | None:
        ...
