from app.etl.dedup import deduplicate_papers, normalize_title, paper_identity
from app.etl.fetchers import FetchedPaper


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
