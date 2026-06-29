from app.repositories.evidence_repository import EvidenceSearchResult
from app.schemas.common import Citation


def build_citation_grounded_answer(
    question: str,
    evidence: list[EvidenceSearchResult],
) -> tuple[str, list[Citation]]:
    if not evidence:
        return (
            "I do not have enough indexed evidence to answer this question yet.",
            [],
        )

    supporting = [item for item in evidence if item.stance == "support"]
    contradicting = [item for item in evidence if item.stance == "contradict"]
    related = [item for item in evidence if item.stance not in {"support", "contradict"}]

    sections = [
        f"Question: {question}",
        _summarize_stance("Supporting evidence", supporting),
        _summarize_stance("Contradicting evidence", contradicting),
        _summarize_stance("Related or weak evidence", related),
        "Limitations: This answer is generated from indexed evidence claims only.",
    ]
    citations = [
        Citation(
            paper_title=item.paper_title,
            url=item.paper_url,
            claim_id=item.claim_id,
            quote=item.evidence_quote,
            confidence=item.confidence,
        )
        for item in evidence
    ]
    return "\n\n".join(section for section in sections if section), citations


def _summarize_stance(label: str, evidence: list[EvidenceSearchResult]) -> str:
    if not evidence:
        return f"{label}: none found."
    bullets = [
        f"- {item.key_finding} ({item.paper_title}; confidence={item.confidence:.2f})"
        for item in evidence
    ]
    return f"{label}:\n" + "\n".join(bullets)
