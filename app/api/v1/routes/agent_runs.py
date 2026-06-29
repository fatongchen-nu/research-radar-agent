from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.schemas.agent_runs import AgentRunCreate, AgentRunRead
from app.services.agent_run_service import AgentRunService, get_agent_run_service

router = APIRouter()


@router.post("", response_model=AgentRunRead, status_code=202)
async def create_agent_run(
    payload: AgentRunCreate,
    service: AgentRunService = Depends(get_agent_run_service),
) -> AgentRunRead:
    return await service.create_run(payload)


@router.get("/{run_id}", response_model=AgentRunRead)
async def get_agent_run(
    run_id: str,
    service: AgentRunService = Depends(get_agent_run_service),
) -> AgentRunRead:
    return await service.get_run(run_id)


@router.get("/{run_id}/events")
async def stream_agent_run_events(
    run_id: str,
    service: AgentRunService = Depends(get_agent_run_service),
) -> StreamingResponse:
    return StreamingResponse(service.stream_events(run_id), media_type="text/event-stream")
