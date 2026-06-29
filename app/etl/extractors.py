from pydantic import BaseModel, Field


class ExtractedEvidence(BaseModel):
    theory: str | None = None
    research_question: str | None = None
    method: str | None = None
    dataset: str | None = None
    key_finding: str
    stance: str = Field(pattern="^(support|contradict|related|weak|unclear)$")
    limitations: str | None = None
    evidence_quote: str
    confidence: float = Field(default=0.5, ge=0, le=1)


class EvidenceExtractor:
    async def extract_from_abstract(self, title: str, abstract: str) -> ExtractedEvidence:
        text = f"{title}\n{abstract}".lower()
        quote = _best_quote(abstract)

        if _mentions_ai_adoption(text) and _contains_all(text, ["forecast", "accuracy"]):
            return ExtractedEvidence(
                theory="AI adoption can improve information processing and forecasting quality.",
                research_question="Does AI adoption improve analyst forecast accuracy?",
                method="Evidence extracted from paper title and abstract.",
                dataset="Not specified in the abstract.",
                key_finding="The paper directly studies whether AI adoption changes analyst forecast accuracy.",
                stance="support",
                limitations="The local sample abstract is synthetic and does not report an effect size.",
                evidence_quote=quote,
                confidence=0.78,
            )

        if _contains_any(text, ["automation", "disclosure"]) and _contains_any(
            text,
            ["investor", "information processing"],
        ):
            return ExtractedEvidence(
                theory="Automation disclosure may relate to market information processing.",
                research_question="Is automation disclosure evidence for AI adoption effects?",
                method="Evidence extracted from paper title and abstract.",
                dataset="Not specified in the abstract.",
                key_finding=(
                    "The paper is related to automation and information processing, but is weaker "
                    "evidence for AI adoption improving analyst forecast accuracy."
                ),
                stance="weak",
                limitations="The abstract is related but does not directly test AI adoption and forecasts.",
                evidence_quote=quote,
                confidence=0.52,
            )

        return ExtractedEvidence(
            research_question=title,
            method="Rule-based abstract extraction.",
            dataset="Not specified in the abstract.",
            key_finding="The abstract is related to the topic but does not provide a clear stance.",
            stance="related",
            limitations="Rule-based extraction is less precise than structured LLM extraction.",
            evidence_quote=quote,
            confidence=0.35,
        )


def _contains_all(text: str, terms: list[str]) -> bool:
    return all(term in text for term in terms)


def _contains_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def _mentions_ai_adoption(text: str) -> bool:
    mentions_ai = "ai" in text.split() or "artificial intelligence" in text
    return mentions_ai and "adoption" in text


def _best_quote(abstract: str) -> str:
    cleaned = " ".join(abstract.split())
    return cleaned[:500] if cleaned else "No abstract text available."
