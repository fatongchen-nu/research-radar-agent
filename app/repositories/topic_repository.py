from typing import Protocol

from app.schemas.topics import TopicProfileCreate, TopicProfileRead


class TopicRepository(Protocol):
    async def create(self, payload: TopicProfileCreate) -> TopicProfileRead:
        ...

    async def list(self, limit: int = 20) -> list[TopicProfileRead]:
        ...

    async def get(self, topic_id: str) -> TopicProfileRead | None:
        ...
