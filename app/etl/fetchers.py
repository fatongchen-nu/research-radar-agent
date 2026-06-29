from dataclasses import dataclass, field


@dataclass(frozen=True)
class FetchedPaper:
    title: str
    authors: list[str] = field(default_factory=list)
    abstract: str | None = None
    source: str = "sample"
    source_id: str | None = None
    url: str | None = None
    doi: str | None = None
    published_at: str | None = None


class SourceFetcher:
    async def fetch(self, keywords: list[str], limit: int) -> list[FetchedPaper]:
        raise NotImplementedError


class SamplePaperFetcher(SourceFetcher):
    async def fetch(self, keywords: list[str], limit: int) -> list[FetchedPaper]:
        topic = ", ".join(keywords) if keywords else "AI adoption"
        return [
            FetchedPaper(
                title=f"Sample evidence paper for {topic}",
                authors=["Sample Author"],
                abstract="This sample abstract is used to keep demos deterministic.",
                source="sample",
                source_id="sample-001",
                url="https://example.com/sample-paper",
            )
        ][:limit]
