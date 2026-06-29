import re

from app.etl.fetchers import FetchedPaper


def normalize_title(title: str) -> str:
    normalized = title.lower().strip()
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def paper_identity(source: str, source_id: str | None, doi: str | None, title: str) -> str:
    if doi:
        return f"doi:{doi.lower().strip()}"
    if source_id:
        return f"{source}:{source_id.strip()}"
    return f"title:{normalize_title(title)}"


def deduplicate_papers(papers: list[FetchedPaper]) -> list[FetchedPaper]:
    seen: set[str] = set()
    deduped: list[FetchedPaper] = []
    for paper in papers:
        identity = paper_identity(
            source=paper.source,
            source_id=paper.source_id,
            doi=paper.doi,
            title=paper.title,
        )
        if identity in seen:
            continue
        seen.add(identity)
        deduped.append(paper)
    return deduped
