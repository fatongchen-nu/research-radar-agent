from app.etl.extractors import EvidenceExtractor, ExtractedEvidence
from app.etl.dedup import deduplicate_papers
from app.etl.fetchers import FetchedPaper, SourceFetcher


class EvidencePipeline:
    def __init__(self, fetcher: SourceFetcher, extractor: EvidenceExtractor) -> None:
        self.fetcher = fetcher
        self.extractor = extractor

    async def run(self, keywords: list[str], limit: int = 20) -> list[tuple[FetchedPaper, ExtractedEvidence]]:
        papers = deduplicate_papers(await self.fetcher.fetch(keywords=keywords, limit=limit))
        results: list[tuple[FetchedPaper, ExtractedEvidence]] = []
        for paper in papers:
            evidence = await self.extractor.extract_from_abstract(
                title=paper.title,
                abstract=paper.abstract or "",
            )
            results.append((paper, evidence))
        return results
