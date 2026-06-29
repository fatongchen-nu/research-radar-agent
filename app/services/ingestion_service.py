from fastapi import Depends

from app.core.errors import AppError
from app.etl.factory import get_evidence_pipeline
from app.etl.pipeline import EvidencePipeline
from app.repositories.dependencies import (
    get_evidence_repository,
    get_ingestion_run_repository,
    get_topic_repository,
)
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.run_repository import IngestionRunRepository
from app.repositories.topic_repository import TopicRepository
from app.schemas.ingestion import IngestionRunRead, IngestionRunStart


class IngestionService:
    def __init__(
        self,
        repository: IngestionRunRepository,
        topic_repository: TopicRepository,
        evidence_repository: EvidenceRepository,
        pipeline: EvidencePipeline,
    ) -> None:
        self.repository = repository
        self.topic_repository = topic_repository
        self.evidence_repository = evidence_repository
        self.pipeline = pipeline

    async def start_run(self, topic_id: str, payload: IngestionRunStart) -> IngestionRunRead:
        topic = await self.topic_repository.get(topic_id)
        if topic is None:
            raise AppError("RESOURCE_NOT_FOUND", "Topic profile not found.", status_code=404)

        run = await self.repository.create(topic_id)
        try:
            keywords = topic.keywords or [topic.research_idea]
            results = await self.pipeline.run(keywords=keywords, limit=payload.source_limit)
            persistence_result = await self.evidence_repository.save_pipeline_results(
                topic_id=topic_id,
                ingestion_run_id=run.id,
                results=results,
            )
            completed = await self.repository.mark_completed(
                run_id=run.id,
                new_papers=persistence_result.new_papers,
                extracted_claims=persistence_result.extracted_claims,
            )
            if completed is None:
                raise AppError("RESOURCE_NOT_FOUND", "Ingestion run not found.", status_code=404)
            return completed
        except Exception as exc:
            failed = await self.repository.mark_failed(
                run.id,
                errors=[{"type": type(exc).__name__, "message": str(exc)}],
            )
            if failed is None:
                raise AppError(
                    "RESOURCE_NOT_FOUND",
                    "Ingestion run not found.",
                    status_code=404,
                ) from exc
            return failed

    async def get_run(self, run_id: str) -> IngestionRunRead:
        run = await self.repository.get(run_id)
        if run is None:
            raise AppError("RESOURCE_NOT_FOUND", "Ingestion run not found.", status_code=404)
        return run


def get_ingestion_service(
    repository: IngestionRunRepository = Depends(get_ingestion_run_repository),
    topic_repository: TopicRepository = Depends(get_topic_repository),
    evidence_repository: EvidenceRepository = Depends(get_evidence_repository),
    pipeline: EvidencePipeline = Depends(get_evidence_pipeline),
) -> IngestionService:
    return IngestionService(repository, topic_repository, evidence_repository, pipeline)
