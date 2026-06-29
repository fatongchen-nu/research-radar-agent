from pydantic import BaseModel, Field


class PaperRead(BaseModel):
    id: str
    title: str
    authors: list[str] = Field(default_factory=list)
    abstract: str | None = None
    source: str
    source_id: str
    url: str | None = None
    published_at: str | None = None


class EvidenceClaimRead(BaseModel):
    id: str
    paper_id: str
    theory: str | None = None
    research_question: str | None = None
    method: str | None = None
    dataset: str | None = None
    key_finding: str
    stance: str
    limitations: str | None = None
    evidence_quote: str
    confidence: float = Field(default=0.5, ge=0, le=1)
