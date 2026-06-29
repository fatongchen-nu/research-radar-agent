from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TopicProfile(Base, TimestampMixin):
    __tablename__ = "topic_profiles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(200))
    research_idea: Mapped[str] = mapped_column(Text)
    keywords: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    seed_papers: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    excluded_terms: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    frequency: Mapped[str] = mapped_column(String(40), default="daily")
    relevance_threshold: Mapped[float] = mapped_column(Numeric(4, 3), default=0.650)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Paper(Base, TimestampMixin):
    __tablename__ = "papers"
    __table_args__ = (UniqueConstraint("source", "source_id", name="uq_papers_source_source_id"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(Text)
    authors: Mapped[list[str]] = mapped_column(ARRAY(Text), default=list)
    abstract: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(80))
    source_id: Mapped[str] = mapped_column(String(200))
    url: Mapped[str | None] = mapped_column(Text)
    doi: Mapped[str | None] = mapped_column(String(200))
    arxiv_id: Mapped[str | None] = mapped_column(String(200))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    normalized_title: Mapped[str] = mapped_column(Text)


class PaperChunk(Base, TimestampMixin):
    __tablename__ = "paper_chunks"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    paper_id: Mapped[UUID] = mapped_column(ForeignKey("papers.id", ondelete="CASCADE"))
    section: Mapped[str] = mapped_column(String(120), default="abstract")
    text: Mapped[str] = mapped_column(Text)


class EvidenceClaim(Base, TimestampMixin):
    __tablename__ = "evidence_claims"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    paper_id: Mapped[UUID] = mapped_column(ForeignKey("papers.id", ondelete="CASCADE"))
    chunk_id: Mapped[UUID | None] = mapped_column(ForeignKey("paper_chunks.id", ondelete="SET NULL"))
    theory: Mapped[str | None] = mapped_column(Text)
    research_question: Mapped[str | None] = mapped_column(Text)
    method: Mapped[str | None] = mapped_column(Text)
    dataset: Mapped[str | None] = mapped_column(Text)
    key_finding: Mapped[str] = mapped_column(Text)
    stance: Mapped[str] = mapped_column(String(40))
    limitations: Mapped[str | None] = mapped_column(Text)
    evidence_quote: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Numeric(4, 3), default=0.500)


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    topic_profile_id: Mapped[UUID] = mapped_column(ForeignKey("topic_profiles.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(40))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    new_papers: Mapped[int] = mapped_column(default=0)
    extracted_claims: Mapped[int] = mapped_column(default=0)
    errors: Mapped[list[dict]] = mapped_column(JSONB, default=list)


class AgentRun(Base, TimestampMixin):
    __tablename__ = "agent_runs"
    __table_args__ = (
        UniqueConstraint("topic_profile_id", "request_id", name="uq_agent_runs_topic_request"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    topic_profile_id: Mapped[UUID] = mapped_column(ForeignKey("topic_profiles.id", ondelete="CASCADE"))
    request_id: Mapped[str] = mapped_column(String(200))
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str | None] = mapped_column(Text)
    citations: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    status: Mapped[str] = mapped_column(String(40))
    token_usage: Mapped[dict] = mapped_column(JSONB, default=dict)
    feedback_score: Mapped[int | None] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DailyDigest(Base, TimestampMixin):
    __tablename__ = "daily_digests"
    __table_args__ = (
        UniqueConstraint("topic_profile_id", "digest_date", name="uq_daily_digests_topic_date"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    topic_profile_id: Mapped[UUID] = mapped_column(ForeignKey("topic_profiles.id", ondelete="CASCADE"))
    digest_date: Mapped[date] = mapped_column(Date)
    summary: Mapped[str] = mapped_column(Text)
    top_papers: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    supporting_claims: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    contradictions: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    recommended_reads: Mapped[list[dict]] = mapped_column(JSONB, default=list)
