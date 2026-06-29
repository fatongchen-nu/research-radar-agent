from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class IngestionRunStart(BaseModel):
    source_limit: int = Field(default=20, ge=1, le=100)
    force_refresh: bool = False


class IngestionRunRead(BaseModel):
    id: str
    topic_profile_id: str
    status: str
    started_at: datetime
    ended_at: datetime | None = None
    new_papers: int = 0
    extracted_claims: int = 0
    errors: list[dict] = Field(default_factory=list)


def ingestion_stub(topic_id: str) -> IngestionRunRead:
    return IngestionRunRead(
        id=str(uuid4()),
        topic_profile_id=topic_id,
        status="queued",
        started_at=datetime.utcnow(),
    )
