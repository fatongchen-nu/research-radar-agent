from app.etl.extractors import EvidenceExtractor
from app.etl.fetchers import ArxivFetcher, FallbackPaperFetcher, SamplePaperFetcher
from app.etl.pipeline import EvidencePipeline


async def main() -> None:
    fetcher = FallbackPaperFetcher(ArxivFetcher(), SamplePaperFetcher())
    pipeline = EvidencePipeline(fetcher, EvidenceExtractor())
    results = await pipeline.run(["AI adoption", "analyst forecast accuracy"], limit=5)
    for paper, evidence in results:
        print({"paper": paper.title, "stance": evidence.stance, "finding": evidence.key_finding})


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
