from app.core.config import settings
from app.etl.extractors import EvidenceExtractor
from app.etl.fetchers import ArxivFetcher, FallbackPaperFetcher, SamplePaperFetcher, SourceFetcher
from app.etl.pipeline import EvidencePipeline


def build_source_fetcher() -> SourceFetcher:
    if settings.paper_fetcher.lower() == "arxiv":
        return FallbackPaperFetcher(ArxivFetcher(), SamplePaperFetcher())
    return SamplePaperFetcher()


def get_evidence_pipeline() -> EvidencePipeline:
    return EvidencePipeline(build_source_fetcher(), EvidenceExtractor())
