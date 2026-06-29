from pydantic import BaseModel, Field

from app.schemas.ingestion import IngestionRunRead
from app.schemas.topics import TopicProfileRead


class DemoIngestionRequest(BaseModel):
    name: str = "AI adoption and analyst forecasts"
    research_idea: str = "AI adoption may improve analyst forecast accuracy."
    keywords: list[str] = Field(default_factory=lambda: ["AI adoption", "forecast accuracy"])
    source_limit: int = Field(default=20, ge=1, le=100)


class DemoIngestionResponse(BaseModel):
    topic: TopicProfileRead
    ingestion_run: IngestionRunRead
