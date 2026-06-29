from app.schemas.common import Citation


class RetrievalService:
    async def search_evidence(self, topic_profile_id: str, question: str) -> list[Citation]:
        _ = topic_profile_id
        _ = question
        return []
