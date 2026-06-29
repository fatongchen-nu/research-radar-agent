from datetime import date
from uuid import uuid4

from pydantic import BaseModel, Field


class DailyDigestRead(BaseModel):
    id: str
    topic_profile_id: str
    digest_date: date
    summary: str
    top_papers: list[dict] = Field(default_factory=list)
    supporting_claims: list[dict] = Field(default_factory=list)
    contradictions: list[dict] = Field(default_factory=list)
    recommended_reads: list[dict] = Field(default_factory=list)


def digest_stub(topic_id: str) -> DailyDigestRead:
    return DailyDigestRead(
        id=str(uuid4()),
        topic_profile_id=topic_id,
        digest_date=date.today(),
        summary="No digest has been generated yet.",
    )
