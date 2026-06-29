from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.models import AgentRun, IngestionRun, TopicProfile
from app.repositories.run_repository import AgentRunRepository, IngestionRunRepository
from app.repositories.topic_repository import TopicRepository
from app.schemas.agent_runs import AgentRunCreate, AgentRunRead
from app.schemas.ingestion import IngestionRunRead
from app.schemas.topics import TopicProfileCreate, TopicProfileRead


def _coerce_uuid(value: str) -> UUID:
    try:
        return UUID(value)
    except ValueError as exc:
        raise AppError("VALIDATION_ERROR", "Invalid UUID.", status_code=400) from exc


def _float(value: Decimal | float) -> float:
    return float(value)


def _topic_to_read(model: TopicProfile) -> TopicProfileRead:
    return TopicProfileRead(
        id=str(model.id),
        name=model.name,
        research_idea=model.research_idea,
        keywords=model.keywords or [],
        seed_papers=model.seed_papers or [],
        excluded_terms=model.excluded_terms or [],
        frequency=model.frequency,
        relevance_threshold=_float(model.relevance_threshold),
        last_run_at=model.last_run_at,
    )


def _ingestion_to_read(model: IngestionRun) -> IngestionRunRead:
    return IngestionRunRead(
        id=str(model.id),
        topic_profile_id=str(model.topic_profile_id),
        status=model.status,
        started_at=model.started_at,
        ended_at=model.ended_at,
        new_papers=model.new_papers,
        extracted_claims=model.extracted_claims,
        errors=model.errors or [],
    )


def _agent_run_to_read(model: AgentRun) -> AgentRunRead:
    return AgentRunRead(
        id=str(model.id),
        topic_profile_id=str(model.topic_profile_id),
        request_id=model.request_id,
        question=model.question,
        answer=model.answer,
        citations=model.citations or [],
        status=model.status,
        token_usage=model.token_usage or {},
        feedback_score=model.feedback_score,
        created_at=model.created_at,
    )


class PostgresTopicRepository(TopicRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, payload: TopicProfileCreate) -> TopicProfileRead:
        model = TopicProfile(**payload.model_dump())
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return _topic_to_read(model)

    async def list(self, limit: int = 20) -> list[TopicProfileRead]:
        result = await self.session.execute(
            select(TopicProfile).order_by(TopicProfile.created_at.desc()).limit(limit)
        )
        return [_topic_to_read(row) for row in result.scalars().all()]

    async def get(self, topic_id: str) -> TopicProfileRead | None:
        model = await self.session.get(TopicProfile, _coerce_uuid(topic_id))
        return _topic_to_read(model) if model else None


class PostgresIngestionRunRepository(IngestionRunRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, topic_id: str) -> IngestionRunRead:
        model = IngestionRun(topic_profile_id=_coerce_uuid(topic_id), status="queued")
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return _ingestion_to_read(model)

    async def get(self, run_id: str) -> IngestionRunRead | None:
        model = await self.session.get(IngestionRun, _coerce_uuid(run_id))
        return _ingestion_to_read(model) if model else None


class PostgresAgentRunRepository(AgentRunRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, payload: AgentRunCreate) -> AgentRunRead:
        model = AgentRun(
            topic_profile_id=_coerce_uuid(payload.topic_profile_id),
            request_id=payload.request_id,
            question=payload.question,
            status="queued",
        )
        self.session.add(model)
        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise AppError(
                "CONFLICT",
                "request_id already exists for this topic profile.",
                status_code=409,
            ) from exc
        await self.session.refresh(model)
        return _agent_run_to_read(model)

    async def get(self, run_id: str) -> AgentRunRead | None:
        model = await self.session.get(AgentRun, _coerce_uuid(run_id))
        return _agent_run_to_read(model) if model else None

    async def find_by_request_id(self, topic_profile_id: str, request_id: str) -> AgentRunRead | None:
        result = await self.session.execute(
            select(AgentRun).where(
                AgentRun.topic_profile_id == _coerce_uuid(topic_profile_id),
                AgentRun.request_id == request_id,
            )
        )
        model = result.scalar_one_or_none()
        return _agent_run_to_read(model) if model else None
