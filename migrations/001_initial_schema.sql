CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS topic_profiles (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    research_idea TEXT NOT NULL,
    keywords TEXT[] NOT NULL DEFAULT '{}',
    seed_papers TEXT[] NOT NULL DEFAULT '{}',
    excluded_terms TEXT[] NOT NULL DEFAULT '{}',
    frequency TEXT NOT NULL DEFAULT 'daily',
    relevance_threshold NUMERIC(4, 3) NOT NULL DEFAULT 0.650,
    last_run_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS papers (
    id UUID PRIMARY KEY,
    title TEXT NOT NULL,
    authors TEXT[] NOT NULL DEFAULT '{}',
    abstract TEXT,
    source TEXT NOT NULL,
    source_id TEXT NOT NULL,
    url TEXT,
    doi TEXT,
    arxiv_id TEXT,
    published_at TIMESTAMPTZ,
    normalized_title TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source, source_id)
);

CREATE INDEX IF NOT EXISTS idx_papers_doi ON papers (doi) WHERE doi IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_papers_arxiv_id ON papers (arxiv_id) WHERE arxiv_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_papers_normalized_title ON papers (normalized_title);

CREATE TABLE IF NOT EXISTS paper_chunks (
    id UUID PRIMARY KEY,
    paper_id UUID NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    section TEXT NOT NULL DEFAULT 'abstract',
    text TEXT NOT NULL,
    embedding vector(1536),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_paper_chunks_paper_id ON paper_chunks (paper_id);

CREATE TABLE IF NOT EXISTS evidence_claims (
    id UUID PRIMARY KEY,
    paper_id UUID NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    chunk_id UUID REFERENCES paper_chunks(id) ON DELETE SET NULL,
    theory TEXT,
    research_question TEXT,
    method TEXT,
    dataset TEXT,
    key_finding TEXT NOT NULL,
    stance TEXT NOT NULL,
    limitations TEXT,
    evidence_quote TEXT NOT NULL,
    confidence NUMERIC(4, 3) NOT NULL DEFAULT 0.500,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_evidence_claims_paper_id ON evidence_claims (paper_id);
CREATE INDEX IF NOT EXISTS idx_evidence_claims_stance ON evidence_claims (stance);

CREATE TABLE IF NOT EXISTS ingestion_runs (
    id UUID PRIMARY KEY,
    topic_profile_id UUID NOT NULL REFERENCES topic_profiles(id) ON DELETE CASCADE,
    status TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at TIMESTAMPTZ,
    new_papers INTEGER NOT NULL DEFAULT 0,
    extracted_claims INTEGER NOT NULL DEFAULT 0,
    errors JSONB NOT NULL DEFAULT '[]'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_ingestion_runs_topic_started
ON ingestion_runs (topic_profile_id, started_at DESC);

CREATE TABLE IF NOT EXISTS agent_runs (
    id UUID PRIMARY KEY,
    topic_profile_id UUID NOT NULL REFERENCES topic_profiles(id) ON DELETE CASCADE,
    request_id TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT,
    citations JSONB NOT NULL DEFAULT '[]'::jsonb,
    status TEXT NOT NULL,
    token_usage JSONB NOT NULL DEFAULT '{}'::jsonb,
    feedback_score INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (topic_profile_id, request_id)
);

CREATE INDEX IF NOT EXISTS idx_agent_runs_topic_created
ON agent_runs (topic_profile_id, created_at DESC);

CREATE TABLE IF NOT EXISTS daily_digests (
    id UUID PRIMARY KEY,
    topic_profile_id UUID NOT NULL REFERENCES topic_profiles(id) ON DELETE CASCADE,
    digest_date DATE NOT NULL,
    summary TEXT NOT NULL,
    top_papers JSONB NOT NULL DEFAULT '[]'::jsonb,
    supporting_claims JSONB NOT NULL DEFAULT '[]'::jsonb,
    contradictions JSONB NOT NULL DEFAULT '[]'::jsonb,
    recommended_reads JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (topic_profile_id, digest_date)
);

CREATE TABLE IF NOT EXISTS evaluation_records (
    id UUID PRIMARY KEY,
    topic_profile_id UUID NOT NULL REFERENCES topic_profiles(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    expected_paper_ids UUID[] NOT NULL DEFAULT '{}',
    expected_stance TEXT,
    expected_quote TEXT,
    observed_agent_run_id UUID REFERENCES agent_runs(id) ON DELETE SET NULL,
    citation_correct BOOLEAN,
    stance_correct BOOLEAN,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
