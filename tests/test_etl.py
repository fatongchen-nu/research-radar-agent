import asyncio

from app.etl.dedup import deduplicate_papers, normalize_title, paper_identity
from app.etl.extractors import ExtractedEvidence
from app.etl.fetchers import FetchedPaper
from app.repositories.memory import MemoryEvidenceRepository


def test_normalize_title_removes_case_and_punctuation() -> None:
    assert normalize_title(" AI Adoption: Forecast Accuracy! ") == "ai adoption forecast accuracy"


def test_paper_identity_prefers_doi() -> None:
    assert paper_identity("arxiv", "1234", "10.123/ABC", "Title") == "doi:10.123/abc"


def test_deduplicate_papers_by_source_id() -> None:
    papers = [
        FetchedPaper(title="A", source="arxiv", source_id="1"),
        FetchedPaper(title="A duplicate", source="arxiv", source_id="1"),
        FetchedPaper(title="B", source="arxiv", source_id="2"),
    ]

    assert len(deduplicate_papers(papers)) == 2


def test_memory_evidence_repository_counts_new_papers_once() -> None:
    repository = MemoryEvidenceRepository()
    paper = FetchedPaper(title="A", source="sample", source_id="1", abstract="Abstract")
    evidence = ExtractedEvidence(
        key_finding="Finding",
        stance="support",
        evidence_quote="Abstract",
    )

    first = asyncio.run(repository.save_pipeline_results("topic-1", "run-1", [(paper, evidence)]))
    second = asyncio.run(repository.save_pipeline_results("topic-1", "run-2", [(paper, evidence)]))

    assert first.new_papers == 1
    assert first.extracted_claims == 1
    assert second.new_papers == 0
    assert second.extracted_claims == 1
