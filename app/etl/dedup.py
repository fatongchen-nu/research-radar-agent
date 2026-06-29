import re


def normalize_title(title: str) -> str:
    normalized = title.lower().strip()
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def paper_identity(source: str, source_id: str | None, doi: str | None, title: str) -> str:
    if doi:
        return f"doi:{doi.lower().strip()}"
    if source_id:
        return f"{source}:{source_id.strip()}"
    return f"title:{normalize_title(title)}"
