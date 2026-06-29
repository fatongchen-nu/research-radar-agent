from fastapi import APIRouter, Depends, Query

from app.schemas.common import ListResponse
from app.schemas.topics import (
    TopicProfileCreate,
    TopicProfileRead,
    TopicProfileRefinementCreate,
    TopicProfileRefinementRead,
)
from app.services.topic_service import TopicService, get_topic_service

router = APIRouter()


@router.post("", response_model=TopicProfileRead, status_code=201)
async def create_topic(
    payload: TopicProfileCreate,
    service: TopicService = Depends(get_topic_service),
) -> TopicProfileRead:
    return await service.create_topic(payload)


@router.get("", response_model=ListResponse[TopicProfileRead])
async def list_topics(
    limit: int = Query(default=20, ge=1, le=100),
    service: TopicService = Depends(get_topic_service),
) -> ListResponse[TopicProfileRead]:
    topics = await service.list_topics(limit=limit)
    return ListResponse(data=topics)


@router.post("/refinements", response_model=TopicProfileRefinementRead)
async def refine_topic_profile(
    payload: TopicProfileRefinementCreate,
    service: TopicService = Depends(get_topic_service),
) -> TopicProfileRefinementRead:
    return await service.refine_topic_profile(payload)


@router.get("/{topic_id}", response_model=TopicProfileRead)
async def get_topic(
    topic_id: str,
    service: TopicService = Depends(get_topic_service),
) -> TopicProfileRead:
    return await service.get_topic(topic_id)
