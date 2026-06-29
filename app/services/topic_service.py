from app.core.errors import AppError
from app.schemas.topics import TopicProfileCreate, TopicProfileRead, topic_stub


class TopicService:
    def __init__(self) -> None:
        self._topics: dict[str, TopicProfileRead] = {}

    async def create_topic(self, payload: TopicProfileCreate) -> TopicProfileRead:
        topic = topic_stub(payload)
        self._topics[topic.id] = topic
        return topic

    async def list_topics(self, limit: int = 20) -> list[TopicProfileRead]:
        return list(self._topics.values())[:limit]

    async def get_topic(self, topic_id: str) -> TopicProfileRead:
        if topic_id not in self._topics:
            raise AppError("RESOURCE_NOT_FOUND", "Topic profile not found.", status_code=404)
        return self._topics[topic_id]


_topic_service = TopicService()


def get_topic_service() -> TopicService:
    return _topic_service
