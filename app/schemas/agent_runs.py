from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field

from app.schemas.common import Citation


class AgentRunCreate(BaseModel):
    topic_profile_id: str
    request_id: str = Field(min_length=8, max_length=200)
    question: str = Field(min_length=5)


class AgentRunRead(BaseModel):
    id: str
    topic_profile_id: str
    request_id: str
    question: str
    answer: str | None = None
    citations: list[Citation] = Field(default_factory=list)
    status: str
    token_usage: dict = Field(default_factory=dict)
    feedback_score: int | None = None
    created_at: datetime


def agent_run_stub(payload: AgentRunCreate) -> AgentRunRead:
    return AgentRunRead(
        id=str(uuid4()),
        topic_profile_id=payload.topic_profile_id,
        request_id=payload.request_id,
        question=payload.question,
        status="queued",
        created_at=datetime.utcnow(),
    )
