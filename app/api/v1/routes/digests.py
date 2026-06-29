from fastapi import APIRouter, Depends

from app.schemas.digests import DailyDigestRead
from app.services.digest_service import DigestService, get_digest_service

router = APIRouter()


@router.get("/topics/{topic_id}/digest/today", response_model=DailyDigestRead)
async def get_today_digest(
    topic_id: str,
    service: DigestService = Depends(get_digest_service),
) -> DailyDigestRead:
    return await service.get_today_digest(topic_id)
