from fastapi import APIRouter, Depends

from app.schemas.ingestion import IngestionRunRead, IngestionRunStart
from app.services.ingestion_service import IngestionService, get_ingestion_service

router = APIRouter()


@router.post("/topics/{topic_id}/ingestion-runs", response_model=IngestionRunRead, status_code=202)
async def start_ingestion_run(
    topic_id: str,
    payload: IngestionRunStart | None = None,
    service: IngestionService = Depends(get_ingestion_service),
) -> IngestionRunRead:
    return await service.start_run(topic_id=topic_id, payload=payload or IngestionRunStart())


@router.get("/ingestion-runs/{run_id}", response_model=IngestionRunRead)
async def get_ingestion_run(
    run_id: str,
    service: IngestionService = Depends(get_ingestion_service),
) -> IngestionRunRead:
    return await service.get_run(run_id)
