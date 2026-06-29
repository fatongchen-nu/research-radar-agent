from pydantic import BaseModel


class EvaluationSummary(BaseModel):
    paper_hit_rate: float = 0.0
    citation_accuracy: float = 0.0
    stance_accuracy: float = 0.0
    claim_extraction_f1: float = 0.0


class EvaluationService:
    async def summarize_topic(self, topic_profile_id: str) -> EvaluationSummary:
        _ = topic_profile_id
        return EvaluationSummary()
