from decimal import Decimal
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.models import (
    AgentRun,
    EvidenceClaim,
    IngestionRun,
    Paper,
    PaperChunk,
    TopicPaper,
    TopicProfile,
)
from app.etl.dedup import normalize_title
from app.etl.extractors import ExtractedEvidence
from app.etl.fetchers import FetchedPaper
from app.repositories.evidence_repository import EvidenceRepository, IngestionPersistenceResult
from app.repositories.evidence_repository import EvidenceSearchResult
from app.repositories.run_repository import AgentRunRepository, IngestionRunRepository
from app.repositories.topic_repository import TopicRepository
from app.schemas.agent_runs import AgentRunCreate, AgentRunRead
from app.schemas.common import Citation
from app.schemas.ingestion import IngestionRunRead
from app.schemas.topics import TopicProfileCreate, TopicProfileRead


def _coerce_uuid(value: str) -> UUID:
    try:
        return UUID(value)
    except ValueError as exc:
        raise AppError("VALIDATION_ERROR", "Invalid UUID.", status_code=400) from exc


def _float(value: Decimal | float) -> float:
    return float(value)


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


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
        citations=[Citation(**citation) for citation in model.citations or []],
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

    async def mark_completed(
        self,
        run_id: str,
        new_papers: int,
        extracted_claims: int,
    ) -> IngestionRunRead | None:
        model = await self.session.get(IngestionRun, _coerce_uuid(run_id))
        if model is None:
            return None
        model.status = "completed"
        model.ended_at = datetime.utcnow()
        model.new_papers = new_papers
        model.extracted_claims = extracted_claims
        await self.session.commit()
        await self.session.refresh(model)
        return _ingestion_to_read(model)

    async def mark_failed(self, run_id: str, errors: list[dict]) -> IngestionRunRead | None:
        model = await self.session.get(IngestionRun, _coerce_uuid(run_id))
        if model is None:
            return None
        model.status = "failed"
        model.ended_at = datetime.utcnow()
        model.errors = errors
        await self.session.commit()
        await self.session.refresh(model)
        return _ingestion_to_read(model)


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

    async def find_by_request_id(
        self,
        topic_profile_id: str,
        request_id: str,
    ) -> AgentRunRead | None:
        result = await self.session.execute(
            select(AgentRun).where(
                AgentRun.topic_profile_id == _coerce_uuid(topic_profile_id),
                AgentRun.request_id == request_id,
            )
        )
        model = result.scalar_one_or_none()
        return _agent_run_to_read(model) if model else None

    async def mark_completed(
        self,
        run_id: str,
        answer: str,
        citations: list[dict],
        token_usage: dict | None = None,
    ) -> AgentRunRead | None:
        model = await self.session.get(AgentRun, _coerce_uuid(run_id))
        if model is None:
            return None
        model.answer = answer
        model.citations = citations
        model.status = "completed"
        model.token_usage = token_usage or {}
        await self.session.commit()
        await self.session.refresh(model)
        return _agent_run_to_read(model)


class PostgresEvidenceRepository(EvidenceRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_pipeline_results(
        self,
        topic_id: str,
        ingestion_run_id: str,
        results: list[tuple[FetchedPaper, ExtractedEvidence]],
    ) -> IngestionPersistenceResult:
        topic_uuid = _coerce_uuid(topic_id)
        run_uuid = _coerce_uuid(ingestion_run_id)
        new_papers = 0
        extracted_claims = 0

        for fetched_paper, evidence in results:
            paper, created = await self._get_or_create_paper(fetched_paper)
            if created:
                new_papers += 1

            await self._ensure_topic_paper(topic_uuid, paper.id, run_uuid)
            chunk = await self._get_or_create_abstract_chunk(paper, fetched_paper.abstract)
            claim_created = await self._create_claim_if_missing(paper, chunk, evidence)
            if claim_created:
                extracted_claims += 1

        await self.session.commit()
        return IngestionPersistenceResult(new_papers, extracted_claims)

    async def _get_or_create_paper(self, fetched_paper: FetchedPaper) -> tuple[Paper, bool]:
        source_id = fetched_paper.source_id or normalize_title(fetched_paper.title)
        result = await self.session.execute(
            select(Paper).where(Paper.source == fetched_paper.source, Paper.source_id == source_id)
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            return existing, False

        paper = Paper(
            title=fetched_paper.title,
            authors=fetched_paper.authors,
            abstract=fetched_paper.abstract,
            source=fetched_paper.source,
            source_id=source_id,
            url=fetched_paper.url,
            doi=fetched_paper.doi,
            arxiv_id=fetched_paper.arxiv_id,
            published_at=_parse_datetime(fetched_paper.published_at),
            normalized_title=normalize_title(fetched_paper.title),
        )
        self.session.add(paper)
        await self.session.flush()
        return paper, True

    async def _ensure_topic_paper(
        self,
        topic_id: UUID,
        paper_id: UUID,
        ingestion_run_id: UUID,
    ) -> None:
        result = await self.session.execute(
            select(TopicPaper).where(
                TopicPaper.topic_profile_id == topic_id,
                TopicPaper.paper_id == paper_id,
            )
        )
        if result.scalar_one_or_none() is not None:
            return

        self.session.add(
            TopicPaper(
                topic_profile_id=topic_id,
                paper_id=paper_id,
                first_seen_run_id=ingestion_run_id,
            )
        )

    async def _get_or_create_abstract_chunk(
        self,
        paper: Paper,
        abstract: str | None,
    ) -> PaperChunk | None:
        text = (abstract or "").strip()
        if not text:
            return None

        result = await self.session.execute(
            select(PaperChunk).where(
                PaperChunk.paper_id == paper.id,
                PaperChunk.section == "abstract",
                PaperChunk.text == text,
            )
        )
        existing = result.scalar_one_or_none()
        if existing is not None:
            return existing

        chunk = PaperChunk(paper_id=paper.id, section="abstract", text=text)
        self.session.add(chunk)
        await self.session.flush()
        return chunk

    async def _create_claim_if_missing(
        self,
        paper: Paper,
        chunk: PaperChunk | None,
        evidence: ExtractedEvidence,
    ) -> bool:
        result = await self.session.execute(
            select(EvidenceClaim).where(
                EvidenceClaim.paper_id == paper.id,
                EvidenceClaim.key_finding == evidence.key_finding,
                EvidenceClaim.evidence_quote == evidence.evidence_quote,
            )
        )
        if result.scalar_one_or_none() is not None:
            return False

        self.session.add(
            EvidenceClaim(
                paper_id=paper.id,
                chunk_id=chunk.id if chunk else None,
                theory=evidence.theory,
                research_question=evidence.research_question,
                method=evidence.method,
                dataset=evidence.dataset,
                key_finding=evidence.key_finding,
                stance=evidence.stance,
                limitations=evidence.limitations,
                evidence_quote=evidence.evidence_quote,
                confidence=evidence.confidence,
            )
        )
        return True

    async def search_claims(
        self,
        topic_id: str,
        question: str,
        limit: int = 5,
    ) -> list[EvidenceSearchResult]:
        result = await self.session.execute(
            select(EvidenceClaim, Paper)
            .join(Paper, EvidenceClaim.paper_id == Paper.id)
            .join(TopicPaper, TopicPaper.paper_id == Paper.id)
            .where(TopicPaper.topic_profile_id == _coerce_uuid(topic_id))
        )
        scored: list[tuple[int, EvidenceClaim, Paper]] = []
        for claim, paper in result.all():
            scored.append((_score_claim(question, claim, paper), claim, paper))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            EvidenceSearchResult(
                claim_id=str(claim.id),
                paper_title=paper.title,
                paper_url=paper.url,
                key_finding=claim.key_finding,
                stance=claim.stance,
                evidence_quote=claim.evidence_quote,
                confidence=float(claim.confidence),
            )
            for _, claim, paper in scored[:limit]
        ]


def _score_claim(question: str, claim: EvidenceClaim, paper: Paper) -> int:
    haystack = " ".join(
        [
            paper.title,
            claim.key_finding,
            claim.evidence_quote,
            claim.stance,
        ]
    ).lower()
    terms = {term.strip(".,?!:;()[]{}").lower() for term in question.split()}
    return sum(1 for term in terms if term and term in haystack)
