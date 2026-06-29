from fastapi import Depends

from app.core.errors import AppError
from app.repositories.dependencies import get_topic_repository
from app.repositories.topic_repository import TopicRepository
from app.schemas.topics import TopicProfileCreate, TopicProfileRead


class TopicService:
    def __init__(self, repository: TopicRepository) -> None:
        self.repository = repository

    async def create_topic(self, payload: TopicProfileCreate) -> TopicProfileRead:
        return await self.repository.create(payload)

    async def list_topics(self, limit: int = 20) -> list[TopicProfileRead]:
        return await self.repository.list(limit=limit)

    async def get_topic(self, topic_id: str) -> TopicProfileRead:
        topic = await self.repository.get(topic_id)
        if topic is None:
            raise AppError("RESOURCE_NOT_FOUND", "Topic profile not found.", status_code=404)
        return topic


def get_topic_service(
    repository: TopicRepository = Depends(get_topic_repository),
) -> TopicService:
    return TopicService(repository)
