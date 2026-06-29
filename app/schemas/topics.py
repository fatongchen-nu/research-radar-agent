from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class TopicProfileCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    research_idea: str = Field(min_length=10)
    keywords: list[str] = Field(default_factory=list)
    seed_papers: list[str] = Field(default_factory=list)
    excluded_terms: list[str] = Field(default_factory=list)
    frequency: str = "daily"
    relevance_threshold: float = Field(default=0.65, ge=0, le=1)


class TopicProfileRead(TopicProfileCreate):
    id: str
    last_run_at: datetime | None = None


def topic_stub(payload: TopicProfileCreate) -> TopicProfileRead:
    return TopicProfileRead(id=str(uuid4()), **payload.model_dump())
