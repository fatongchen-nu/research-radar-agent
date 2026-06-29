CREATE TABLE IF NOT EXISTS topic_papers (
    id UUID PRIMARY KEY,
    topic_profile_id UUID NOT NULL REFERENCES topic_profiles(id) ON DELETE CASCADE,
    paper_id UUID NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    relevance_score NUMERIC(4, 3) NOT NULL DEFAULT 0.500,
    first_seen_run_id UUID REFERENCES ingestion_runs(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (topic_profile_id, paper_id)
);

CREATE INDEX IF NOT EXISTS idx_topic_papers_topic
ON topic_papers (topic_profile_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_topic_papers_paper
ON topic_papers (paper_id);
