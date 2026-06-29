from app.schemas.topics import TopicProfileCreate, TopicProfileRead


class TopicRepository:
    async def create(self, payload: TopicProfileCreate) -> TopicProfileRead:
        raise NotImplementedError

    async def list(self, limit: int = 20) -> list[TopicProfileRead]:
        raise NotImplementedError

    async def get(self, topic_id: str) -> TopicProfileRead | None:
        raise NotImplementedError
