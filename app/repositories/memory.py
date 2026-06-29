from datetime import datetime
from dataclasses import dataclass
from uuid import uuid4

from app.etl.dedup import paper_identity
from app.etl.extractors import ExtractedEvidence
from app.etl.fetchers import FetchedPaper
from app.repositories.evidence_repository import (
    EvidenceRepository,
    EvidenceSearchResult,
    IngestionPersistenceResult,
)
from app.repositories.run_repository import AgentRunRepository, IngestionRunRepository
from app.repositories.topic_repository import TopicRepository
from app.schemas.agent_runs import AgentRunCreate, AgentRunRead
from app.schemas.common import Citation
from app.schemas.ingestion import IngestionRunRead
from app.schemas.topics import TopicProfileCreate, TopicProfileRead


class MemoryTopicRepository(TopicRepository):
    def __init__(self) -> None:
        self._topics: dict[str, TopicProfileRead] = {}

    async def create(self, payload: TopicProfileCreate) -> TopicProfileRead:
        topic = TopicProfileRead(id=str(uuid4()), **payload.model_dump())
        self._topics[topic.id] = topic
        return topic

    async def list(self, limit: int = 20) -> list[TopicProfileRead]:
        return list(self._topics.values())[:limit]

    async def get(self, topic_id: str) -> TopicProfileRead | None:
        return self._topics.get(topic_id)


class MemoryIngestionRunRepository(IngestionRunRepository):
    def __init__(self) -> None:
        self._runs: dict[str, IngestionRunRead] = {}

    async def create(self, topic_id: str) -> IngestionRunRead:
        run = IngestionRunRead(
            id=str(uuid4()),
            topic_profile_id=topic_id,
            status="queued",
            started_at=datetime.utcnow(),
        )
        self._runs[run.id] = run
        return run

    async def get(self, run_id: str) -> IngestionRunRead | None:
        return self._runs.get(run_id)

    async def mark_completed(
        self,
        run_id: str,
        new_papers: int,
        extracted_claims: int,
    ) -> IngestionRunRead | None:
        run = self._runs.get(run_id)
        if run is None:
            return None
        completed = run.model_copy(
            update={
                "status": "completed",
                "ended_at": datetime.utcnow(),
                "new_papers": new_papers,
                "extracted_claims": extracted_claims,
            }
        )
        self._runs[run_id] = completed
        return completed

    async def mark_failed(self, run_id: str, errors: list[dict]) -> IngestionRunRead | None:
        run = self._runs.get(run_id)
        if run is None:
            return None
        failed = run.model_copy(
            update={
                "status": "failed",
                "ended_at": datetime.utcnow(),
                "errors": errors,
            }
        )
        self._runs[run_id] = failed
        return failed


class MemoryAgentRunRepository(AgentRunRepository):
    def __init__(self) -> None:
        self._runs: dict[str, AgentRunRead] = {}

    async def create(self, payload: AgentRunCreate) -> AgentRunRead:
        run = AgentRunRead(
            id=str(uuid4()),
            topic_profile_id=payload.topic_profile_id,
            request_id=payload.request_id,
            question=payload.question,
            status="queued",
            created_at=datetime.utcnow(),
        )
        self._runs[run.id] = run
        return run

    async def get(self, run_id: str) -> AgentRunRead | None:
        return self._runs.get(run_id)

    async def find_by_request_id(
        self,
        topic_profile_id: str,
        request_id: str,
    ) -> AgentRunRead | None:
        for run in self._runs.values():
            if run.topic_profile_id == topic_profile_id and run.request_id == request_id:
                return run
        return None

    async def mark_completed(
        self,
        run_id: str,
        answer: str,
        citations: list[dict],
        token_usage: dict | None = None,
    ) -> AgentRunRead | None:
        run = self._runs.get(run_id)
        if run is None:
            return None
        completed = run.model_copy(
            update={
                "answer": answer,
                "citations": [Citation(**citation) for citation in citations],
                "status": "completed",
                "token_usage": token_usage or {},
            }
        )
        self._runs[run_id] = completed
        return completed


@dataclass(frozen=True)
class MemoryStoredClaim:
    topic_id: str
    paper_identity: str
    claim_id: str
    paper_title: str
    paper_url: str | None
    evidence: ExtractedEvidence


class MemoryEvidenceRepository(EvidenceRepository):
    def __init__(self) -> None:
        self._paper_identities: set[str] = set()
        self._claims: list[MemoryStoredClaim] = []
        self._claim_keys: set[tuple[str, str, str, str]] = set()
        self._topic_papers: set[tuple[str, str]] = set()

    async def save_pipeline_results(
        self,
        topic_id: str,
        ingestion_run_id: str,
        results: list[tuple[FetchedPaper, ExtractedEvidence]],
    ) -> IngestionPersistenceResult:
        _ = ingestion_run_id
        new_papers = 0
        extracted_claims = 0

        for paper, evidence in results:
            identity = paper_identity(paper.source, paper.source_id, paper.doi, paper.title)
            if identity not in self._paper_identities:
                self._paper_identities.add(identity)
                new_papers += 1

            topic_paper_key = (topic_id, identity)
            self._topic_papers.add(topic_paper_key)
            claim_key = (topic_id, identity, evidence.key_finding, evidence.evidence_quote)
            if claim_key not in self._claim_keys:
                self._claim_keys.add(claim_key)
                self._claims.append(
                    MemoryStoredClaim(
                        topic_id=topic_id,
                        paper_identity=identity,
                        claim_id=str(uuid4()),
                        paper_title=paper.title,
                        paper_url=paper.url,
                        evidence=evidence,
                    )
                )
                extracted_claims += 1

        return IngestionPersistenceResult(
            new_papers=new_papers,
            extracted_claims=extracted_claims,
        )

    async def search_claims(
        self,
        topic_id: str,
        question: str,
        limit: int = 5,
    ) -> list[EvidenceSearchResult]:
        scored = [
            (_score_claim(question, claim), claim)
            for claim in self._claims
            if claim.topic_id == topic_id
        ]
        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            EvidenceSearchResult(
                claim_id=claim.claim_id,
                paper_title=claim.paper_title,
                paper_url=claim.paper_url,
                key_finding=claim.evidence.key_finding,
                stance=claim.evidence.stance,
                evidence_quote=claim.evidence.evidence_quote,
                confidence=claim.evidence.confidence,
            )
            for _, claim in scored[:limit]
        ]


def _score_claim(question: str, claim: MemoryStoredClaim) -> int:
    haystack = " ".join(
        [
            claim.paper_title,
            claim.evidence.key_finding,
            claim.evidence.evidence_quote,
            claim.evidence.stance,
        ]
    ).lower()
    terms = {term.strip(".,?!:;()[]{}").lower() for term in question.split()}
    return sum(1 for term in terms if term and term in haystack)


memory_topic_repository = MemoryTopicRepository()
memory_ingestion_run_repository = MemoryIngestionRunRepository()
memory_agent_run_repository = MemoryAgentRunRepository()
memory_evidence_repository = MemoryEvidenceRepository()
