from fastapi import Depends

from app.core.errors import AppError
from app.repositories.dependencies import get_ingestion_run_repository
from app.repositories.run_repository import IngestionRunRepository
from app.schemas.ingestion import IngestionRunRead, IngestionRunStart


class IngestionService:
    def __init__(self, repository: IngestionRunRepository) -> None:
        self.repository = repository

    async def start_run(self, topic_id: str, payload: IngestionRunStart) -> IngestionRunRead:
        _ = payload
        return await self.repository.create(topic_id)

    async def get_run(self, run_id: str) -> IngestionRunRead:
        run = await self.repository.get(run_id)
        if run is None:
            raise AppError("RESOURCE_NOT_FOUND", "Ingestion run not found.", status_code=404)
        return run


def get_ingestion_service(
    repository: IngestionRunRepository = Depends(get_ingestion_run_repository),
) -> IngestionService:
    return IngestionService(repository)
