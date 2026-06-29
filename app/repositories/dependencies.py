from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db_session
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.memory import (
    memory_agent_run_repository,
    memory_evidence_repository,
    memory_ingestion_run_repository,
    memory_topic_repository,
)
from app.repositories.postgres import (
    PostgresAgentRunRepository,
    PostgresEvidenceRepository,
    PostgresIngestionRunRepository,
    PostgresTopicRepository,
)
from app.repositories.run_repository import AgentRunRepository, IngestionRunRepository
from app.repositories.topic_repository import TopicRepository


async def get_optional_db_session() -> AsyncGenerator[AsyncSession | None, None]:
    if settings.repository_backend != "postgres":
        yield None
        return

    async for session in get_db_session():
        yield session


def get_topic_repository(
    session: AsyncSession | None = Depends(get_optional_db_session),
) -> TopicRepository:
    if settings.repository_backend == "postgres":
        if session is None:
            raise RuntimeError("Postgres repository selected without a database session.")
        return PostgresTopicRepository(session)
    return memory_topic_repository


def get_ingestion_run_repository(
    session: AsyncSession | None = Depends(get_optional_db_session),
) -> IngestionRunRepository:
    if settings.repository_backend == "postgres":
        if session is None:
            raise RuntimeError("Postgres repository selected without a database session.")
        return PostgresIngestionRunRepository(session)
    return memory_ingestion_run_repository


def get_agent_run_repository(
    session: AsyncSession | None = Depends(get_optional_db_session),
) -> AgentRunRepository:
    if settings.repository_backend == "postgres":
        if session is None:
            raise RuntimeError("Postgres repository selected without a database session.")
        return PostgresAgentRunRepository(session)
    return memory_agent_run_repository


def get_evidence_repository(
    session: AsyncSession | None = Depends(get_optional_db_session),
) -> EvidenceRepository:
    if settings.repository_backend == "postgres":
        if session is None:
            raise RuntimeError("Postgres repository selected without a database session.")
        return PostgresEvidenceRepository(session)
    return memory_evidence_repository
