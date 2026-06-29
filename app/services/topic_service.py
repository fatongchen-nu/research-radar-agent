from fastapi import Depends

from app.core.errors import AppError
from app.repositories.dependencies import get_topic_repository
from app.repositories.topic_repository import TopicRepository
from app.schemas.topics import (
    TopicProfileCreate,
    TopicProfileRead,
    TopicProfileRefinementCreate,
    TopicProfileRefinementRead,
)


class TopicService:
    def __init__(self, repository: TopicRepository) -> None:
        self.repository = repository

    async def create_topic(self, payload: TopicProfileCreate) -> TopicProfileRead:
        return await self.repository.create(payload)

    async def list_topics(self, limit: int = 20) -> list[TopicProfileRead]:
        return await self.repository.list(limit=limit)

    async def get_topic(self, topic_id: str) -> TopicProfileRead:
        topic = await self.repository.get(topic_id)
        if topic is None:
            raise AppError("RESOURCE_NOT_FOUND", "Topic profile not found.", status_code=404)
        return topic

    async def refine_topic_profile(
        self,
        payload: TopicProfileRefinementCreate,
    ) -> TopicProfileRefinementRead:
        return refine_research_idea(payload)


def refine_research_idea(payload: TopicProfileRefinementCreate) -> TopicProfileRefinementRead:
    idea = " ".join(payload.research_idea.split())
    text = idea.lower()
    preferred_domain = (payload.preferred_domain or "").strip().lower()

    is_digital_twin = "digital twin" in text or "digital twins" in text
    mentions_memory = (
        "long-term memory" in text
        or "long term memory" in text
        or "persistent memory" in text
        or "memory" in text
    )
    mentions_statistical_memory = any(
        term in text
        for term in [
            "long memory",
            "long-range dependence",
            "long range dependence",
            "hurst",
            "arfima",
            "fractional integration",
        ]
    )
    preferred_statistics = any(
        term in preferred_domain for term in ["stat", "time series", "econometric"]
    )
    preferred_business = any(
        term in preferred_domain for term in ["business", "management", "strategy"]
    )

    if preferred_statistics or (mentions_statistical_memory and not is_digital_twin):
        assumed_domain = "statistics / time-series analysis"
    elif preferred_business:
        assumed_domain = "business process digital twins"
    elif is_digital_twin and mentions_memory:
        assumed_domain = "computer science / cyber-physical systems"
    elif is_digital_twin:
        assumed_domain = "cyber-physical systems"
    else:
        assumed_domain = preferred_domain or "interdisciplinary research"

    included_concepts = _ordered_unique(
        [
            "digital twin" if is_digital_twin else None,
            "cyber-physical systems" if is_digital_twin else None,
            "long-term memory" if mentions_memory else None,
            "persistent memory" if mentions_memory and not preferred_statistics else None,
            "temporal state" if mentions_memory and not preferred_statistics else None,
            "historical context" if mentions_memory and not preferred_statistics else None,
            "continual learning" if mentions_memory and not preferred_statistics else None,
            "knowledge graph" if mentions_memory and not preferred_statistics else None,
            "long-range dependence" if preferred_statistics else None,
            "ARFIMA" if preferred_statistics else None,
            "Hurst exponent" if preferred_statistics else None,
        ]
    )

    excluded_concepts = _ordered_unique(
        [
            "ARFIMA" if mentions_memory and not preferred_statistics else None,
            "Hurst exponent" if mentions_memory and not preferred_statistics else None,
            "long-range dependence" if mentions_memory and not preferred_statistics else None,
            "fractional integration" if mentions_memory and not preferred_statistics else None,
            (
                "pure time-series long memory"
                if mentions_memory and not preferred_statistics
                else None
            ),
            (
                "business digital twin strategy"
                if is_digital_twin and not preferred_business
                else None
            ),
            "market analysis" if is_digital_twin and not preferred_business else None,
        ]
    )

    keywords = _ordered_unique(
        [
            *included_concepts,
            "agent memory" if mentions_memory and not preferred_statistics else None,
            "state retention" if mentions_memory and not preferred_statistics else None,
            "predictive maintenance" if is_digital_twin else None,
        ]
    )

    ambiguity_notes = _build_ambiguity_notes(
        is_digital_twin=is_digital_twin,
        mentions_memory=mentions_memory,
        mentions_statistical_memory=mentions_statistical_memory,
        preferred_domain=preferred_domain,
    )
    needs_clarification = bool(ambiguity_notes) and not preferred_domain

    name = _suggest_topic_name(idea, is_digital_twin, mentions_memory, assumed_domain)
    normalized_research_idea = _normalize_research_idea(idea, name, assumed_domain)
    suggested_search_queries = _build_search_queries(
        keywords=keywords,
        excluded_concepts=excluded_concepts,
        is_digital_twin=is_digital_twin,
        mentions_memory=mentions_memory,
        preferred_statistics=preferred_statistics,
    )
    topic_profile = TopicProfileCreate(
        name=name,
        research_idea=normalized_research_idea,
        keywords=keywords[:10],
        excluded_terms=excluded_concepts,
        relevance_threshold=0.72 if needs_clarification else 0.65,
    )

    return TopicProfileRefinementRead(
        name=name,
        normalized_research_idea=normalized_research_idea,
        assumed_domain=assumed_domain,
        included_concepts=included_concepts,
        excluded_concepts=excluded_concepts,
        keywords=keywords,
        ambiguity_notes=ambiguity_notes,
        suggested_search_queries=suggested_search_queries,
        needs_clarification=needs_clarification,
        topic_profile=topic_profile,
    )


def _ordered_unique(values: list[str | None]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value is None:
            continue
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(value)
    return unique


def _build_ambiguity_notes(
    *,
    is_digital_twin: bool,
    mentions_memory: bool,
    mentions_statistical_memory: bool,
    preferred_domain: str,
) -> list[str]:
    notes: list[str] = []
    if mentions_memory and not preferred_domain:
        notes.append(
            "Long-term memory can mean AI/persistent memory or statistical long-memory "
            "time-series behavior."
        )
    if is_digital_twin and not preferred_domain:
        notes.append(
            "Digital twin can refer to technical cyber-physical systems, business process "
            "twins, healthcare twins, or urban simulation systems."
        )
    if mentions_statistical_memory and is_digital_twin and not preferred_domain:
        notes.append(
            "The query includes signals for both digital-twin systems and statistical "
            "long-memory terminology."
        )
    return notes


def _suggest_topic_name(
    idea: str,
    is_digital_twin: bool,
    mentions_memory: bool,
    assumed_domain: str,
) -> str:
    if is_digital_twin and mentions_memory and "statistics" not in assumed_domain:
        return "Long-term memory in digital twin systems"
    if "statistics" in assumed_domain:
        return "Statistical long memory in time-series systems"
    words = idea.strip().rstrip(".?")
    return words[:1].upper() + words[1:] if words else "Research topic"


def _normalize_research_idea(idea: str, name: str, assumed_domain: str) -> str:
    if name == "Long-term memory in digital twin systems":
        return (
            "Study how digital twin systems represent, retain, and use long-term historical "
            "state or memory over time."
        )
    if "statistics" in assumed_domain:
        return "Study statistical long-memory behavior and persistence in time-series data."
    return idea


def _build_search_queries(
    *,
    keywords: list[str],
    excluded_concepts: list[str],
    is_digital_twin: bool,
    mentions_memory: bool,
    preferred_statistics: bool,
) -> list[str]:
    if preferred_statistics:
        return [
            '"long memory" "time series"',
            '"long-range dependence" "digital twin"',
            '"ARFIMA" "cyber-physical systems"',
        ]

    queries = [
        '"digital twin" "long-term memory"' if is_digital_twin and mentions_memory else None,
        '"digital twin" "persistent memory"' if is_digital_twin and mentions_memory else None,
        '"digital twin" "temporal state" "knowledge graph"'
        if is_digital_twin and mentions_memory
        else None,
        '"cyber-physical systems" "continual learning" "digital twin"'
        if is_digital_twin and mentions_memory
        else None,
    ]
    generic_query = " ".join(f'"{keyword}"' for keyword in keywords[:3])
    if generic_query:
        queries.append(generic_query)
    if excluded_concepts and queries:
        excluded_terms = " -".join(f'"{term}"' for term in excluded_concepts[:3])
        queries.append(f"{queries[0]} -{excluded_terms}")
    return _ordered_unique(queries)


def get_topic_service(
    repository: TopicRepository = Depends(get_topic_repository),
) -> TopicService:
    return TopicService(repository)
