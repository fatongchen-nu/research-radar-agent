from app.core.errors import AppError
from app.schemas.ingestion import IngestionRunRead, IngestionRunStart, ingestion_stub


class IngestionService:
    def __init__(self) -> None:
        self._runs: dict[str, IngestionRunRead] = {}

    async def start_run(self, topic_id: str, payload: IngestionRunStart) -> IngestionRunRead:
        _ = payload
        run = ingestion_stub(topic_id)
        self._runs[run.id] = run
        return run

    async def get_run(self, run_id: str) -> IngestionRunRead:
        if run_id not in self._runs:
            raise AppError("RESOURCE_NOT_FOUND", "Ingestion run not found.", status_code=404)
        return self._runs[run_id]


_ingestion_service = IngestionService()


def get_ingestion_service() -> IngestionService:
    return _ingestion_service
