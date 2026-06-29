from datetime import datetime
from uuid import uuid4

from app.repositories.run_repository import AgentRunRepository, IngestionRunRepository
from app.repositories.topic_repository import TopicRepository
from app.schemas.agent_runs import AgentRunCreate, AgentRunRead
from app.schemas.ingestion import IngestionRunRead
from app.schemas.topics import TopicProfileCreate, TopicProfileRead


class MemoryTopicRepository(TopicRepository):
    def __init__(self) -> None:
        self._topics: dict[str, TopicProfileRead] = {}

    async def create(self, payload: TopicProfileCreate) -> TopicProfileRead:
        topic = TopicProfileRead(id=str(uuid4()), **payload.model_dump())
        self._topics[topic.id] = topic
        return topic

    async def list(self, limit: int = 20) -> list[TopicProfileRead]:
        return list(self._topics.values())[:limit]

    async def get(self, topic_id: str) -> TopicProfileRead | None:
        return self._topics.get(topic_id)


class MemoryIngestionRunRepository(IngestionRunRepository):
    def __init__(self) -> None:
        self._runs: dict[str, IngestionRunRead] = {}

    async def create(self, topic_id: str) -> IngestionRunRead:
        run = IngestionRunRead(
            id=str(uuid4()),
            topic_profile_id=topic_id,
            status="queued",
            started_at=datetime.utcnow(),
        )
        self._runs[run.id] = run
        return run

    async def get(self, run_id: str) -> IngestionRunRead | None:
        return self._runs.get(run_id)


class MemoryAgentRunRepository(AgentRunRepository):
    def __init__(self) -> None:
        self._runs: dict[str, AgentRunRead] = {}

    async def create(self, payload: AgentRunCreate) -> AgentRunRead:
        run = AgentRunRead(
            id=str(uuid4()),
            topic_profile_id=payload.topic_profile_id,
            request_id=payload.request_id,
            question=payload.question,
            status="queued",
            created_at=datetime.utcnow(),
        )
        self._runs[run.id] = run
        return run

    async def get(self, run_id: str) -> AgentRunRead | None:
        return self._runs.get(run_id)

    async def find_by_request_id(self, topic_profile_id: str, request_id: str) -> AgentRunRead | None:
        for run in self._runs.values():
            if run.topic_profile_id == topic_profile_id and run.request_id == request_id:
                return run
        return None


memory_topic_repository = MemoryTopicRepository()
memory_ingestion_run_repository = MemoryIngestionRunRepository()
memory_agent_run_repository = MemoryAgentRunRepository()
