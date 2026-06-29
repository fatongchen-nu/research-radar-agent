from dataclasses import dataclass
from typing import Protocol

from app.etl.extractors import ExtractedEvidence
from app.etl.fetchers import FetchedPaper


@dataclass(frozen=True)
class IngestionPersistenceResult:
    new_papers: int
    extracted_claims: int


class EvidenceRepository(Protocol):
    async def save_pipeline_results(
        self,
        topic_id: str,
        ingestion_run_id: str,
        results: list[tuple[FetchedPaper, ExtractedEvidence]],
    ) -> IngestionPersistenceResult:
        ...
