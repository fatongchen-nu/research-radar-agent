from pydantic import BaseModel, Field


class ExtractedEvidence(BaseModel):
    theory: str | None = None
    research_question: str | None = None
    method: str | None = None
    dataset: str | None = None
    key_finding: str
    stance: str = Field(pattern="^(support|contradict|related|weak|unclear)$")
    limitations: str | None = None
    evidence_quote: str
    confidence: float = Field(default=0.5, ge=0, le=1)


class EvidenceExtractor:
    async def extract_from_abstract(self, title: str, abstract: str) -> ExtractedEvidence:
        return ExtractedEvidence(
            research_question=title,
            key_finding="Evidence extraction LLM integration is not wired yet.",
            stance="unclear",
            limitations="This is a deterministic placeholder extraction.",
            evidence_quote=abstract[:500],
            confidence=0.1,
        )
