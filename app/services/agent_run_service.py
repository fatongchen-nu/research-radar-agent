import asyncio
import json
from collections.abc import AsyncIterator

from fastapi import Depends

from app.core.errors import AppError
from app.repositories.dependencies import get_agent_run_repository, get_evidence_repository
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.run_repository import AgentRunRepository
from app.schemas.agent_runs import AgentRunCreate, AgentRunRead
from app.services.answer_service import build_citation_grounded_answer


class AgentRunService:
    def __init__(
        self,
        repository: AgentRunRepository,
        evidence_repository: EvidenceRepository,
    ) -> None:
        self.repository = repository
        self.evidence_repository = evidence_repository

    async def create_run(self, payload: AgentRunCreate) -> AgentRunRead:
        existing = await self.repository.find_by_request_id(
            payload.topic_profile_id,
            payload.request_id,
        )
        if existing is not None:
            raise AppError(
                "CONFLICT",
                "request_id already exists for this topic profile.",
                status_code=409,
            )

        run = await self.repository.create(payload)
        evidence = await self.evidence_repository.search_claims(
            topic_id=payload.topic_profile_id,
            question=payload.question,
        )
        answer, citations = build_citation_grounded_answer(payload.question, evidence)
        completed = await self.repository.mark_completed(
            run_id=run.id,
            answer=answer,
            citations=[citation.model_dump() for citation in citations],
            token_usage={"retrieved_claims": len(evidence), "llm_tokens": 0},
        )
        if completed is None:
            raise AppError("RESOURCE_NOT_FOUND", "Agent run not found.", status_code=404)
        return completed

    async def get_run(self, run_id: str) -> AgentRunRead:
        run = await self.repository.get(run_id)
        if run is None:
            raise AppError("RESOURCE_NOT_FOUND", "Agent run not found.", status_code=404)
        return run

    async def stream_events(self, run_id: str) -> AsyncIterator[str]:
        run = await self.get_run(run_id)
        events = [
            {"type": "run.started", "run_id": run.id},
            {
                "type": "retrieval.completed",
                "retrieved_claims": run.token_usage.get("retrieved_claims", 0),
            },
            {
                "type": "answer.completed",
                "answer": run.answer,
                "citations": [
                    citation.model_dump() if hasattr(citation, "model_dump") else citation
                    for citation in run.citations
                ],
            },
            {"type": "run.completed", "status": run.status},
        ]
        for event in events:
            yield f"data: {json.dumps(event)}\n\n"
            await asyncio.sleep(0.05)


def get_agent_run_service(
    repository: AgentRunRepository = Depends(get_agent_run_repository),
    evidence_repository: EvidenceRepository = Depends(get_evidence_repository),
) -> AgentRunService:
    return AgentRunService(repository, evidence_repository)
