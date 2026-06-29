from dataclasses import dataclass
from typing import Protocol

from app.etl.extractors import ExtractedEvidence
from app.etl.fetchers import FetchedPaper


@dataclass(frozen=True)
class IngestionPersistenceResult:
    new_papers: int
    extracted_claims: int


@dataclass(frozen=True)
class EvidenceSearchResult:
    claim_id: str
    paper_title: str
    paper_url: str | None
    key_finding: str
    stance: str
    evidence_quote: str
    confidence: float


class EvidenceRepository(Protocol):
    async def save_pipeline_results(
        self,
        topic_id: str,
        ingestion_run_id: str,
        results: list[tuple[FetchedPaper, ExtractedEvidence]],
    ) -> IngestionPersistenceResult:
        ...

    async def search_claims(
        self,
        topic_id: str,
        question: str,
        limit: int = 5,
    ) -> list[EvidenceSearchResult]:
        ...
