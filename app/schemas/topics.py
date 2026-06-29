from datetime import datetime

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


class TopicProfileRefinementCreate(BaseModel):
    research_idea: str = Field(min_length=10)
    preferred_domain: str | None = Field(
        default=None,
        description=(
            "Optional user hint such as computer science, statistics, healthcare, "
            "or business."
        ),
    )


class TopicProfileRefinementRead(BaseModel):
    name: str
    normalized_research_idea: str
    assumed_domain: str
    included_concepts: list[str]
    excluded_concepts: list[str]
    keywords: list[str]
    ambiguity_notes: list[str]
    suggested_search_queries: list[str]
    needs_clarification: bool
    topic_profile: TopicProfileCreate
