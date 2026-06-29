from app.schemas.agent_runs import AgentRunCreate, AgentRunRead
from app.schemas.ingestion import IngestionRunRead


class AgentRunRepository:
    async def create(self, payload: AgentRunCreate) -> AgentRunRead:
        raise NotImplementedError

    async def get(self, run_id: str) -> AgentRunRead | None:
        raise NotImplementedError


class IngestionRunRepository:
    async def create(self, topic_id: str) -> IngestionRunRead:
        raise NotImplementedError

    async def get(self, run_id: str) -> IngestionRunRead | None:
        raise NotImplementedError
