import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlencode

import httpx


@dataclass(frozen=True)
class FetchedPaper:
    title: str
    authors: list[str] = field(default_factory=list)
    abstract: str | None = None
    source: str = "sample"
    source_id: str | None = None
    url: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    published_at: str | None = None


class SourceFetcher:
    async def fetch(self, keywords: list[str], limit: int) -> list[FetchedPaper]:
        raise NotImplementedError


class SamplePaperFetcher(SourceFetcher):
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path("data/sample/papers.json")

    async def fetch(self, keywords: list[str], limit: int) -> list[FetchedPaper]:
        if self.path.exists():
            rows = json.loads(self.path.read_text())
            return [
                FetchedPaper(
                    title=row["title"],
                    authors=row.get("authors", []),
                    abstract=row.get("abstract"),
                    source=row.get("source", "sample"),
                    source_id=row.get("source_id"),
                    url=row.get("url"),
                    doi=row.get("doi"),
                    arxiv_id=row.get("arxiv_id"),
                    published_at=row.get("published_at"),
                )
                for row in rows[:limit]
            ]

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


class ArxivFetcher(SourceFetcher):
    base_url = "https://export.arxiv.org/api/query"
    atom_namespace = {"atom": "http://www.w3.org/2005/Atom"}

    def __init__(self, client: httpx.AsyncClient | None = None, timeout_seconds: float = 20.0) -> None:
        self.client = client
        self.timeout_seconds = timeout_seconds

    async def fetch(self, keywords: list[str], limit: int) -> list[FetchedPaper]:
        query = self._build_query(keywords)
        params = urlencode(
            {
                "search_query": query,
                "start": 0,
                "max_results": limit,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
            }
        )
        url = f"{self.base_url}?{params}"

        if self.client is not None:
            response = await self.client.get(url, timeout=self.timeout_seconds)
            response.raise_for_status()
            return self._parse(response.text)

        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=self.timeout_seconds)
            response.raise_for_status()
            return self._parse(response.text)

    def _build_query(self, keywords: list[str]) -> str:
        terms = [term.strip() for term in keywords if term.strip()]
        if not terms:
            return "all:artificial intelligence"
        return " OR ".join(f'all:"{term}"' for term in terms)

    def _parse(self, xml_text: str) -> list[FetchedPaper]:
        root = ET.fromstring(xml_text)
        papers: list[FetchedPaper] = []
        for entry in root.findall("atom:entry", self.atom_namespace):
            title = self._text(entry, "atom:title")
            source_id = self._text(entry, "atom:id")
            arxiv_id = source_id.rsplit("/", maxsplit=1)[-1] if source_id else None
            authors = [
                self._text(author, "atom:name")
                for author in entry.findall("atom:author", self.atom_namespace)
            ]
            papers.append(
                FetchedPaper(
                    title=" ".join(title.split()),
                    authors=[author for author in authors if author],
                    abstract=self._text(entry, "atom:summary"),
                    source="arxiv",
                    source_id=arxiv_id,
                    url=source_id,
                    arxiv_id=arxiv_id,
                    published_at=self._text(entry, "atom:published"),
                )
            )
        return papers

    def _text(self, node: ET.Element, path: str) -> str:
        found = node.find(path, self.atom_namespace)
        return found.text.strip() if found is not None and found.text else ""


class FallbackPaperFetcher(SourceFetcher):
    def __init__(self, primary: SourceFetcher, fallback: SourceFetcher) -> None:
        self.primary = primary
        self.fallback = fallback

    async def fetch(self, keywords: list[str], limit: int) -> list[FetchedPaper]:
        try:
            papers = await self.primary.fetch(keywords, limit)
        except httpx.HTTPError:
            return await self.fallback.fetch(keywords, limit)
        return papers or await self.fallback.fetch(keywords, limit)
