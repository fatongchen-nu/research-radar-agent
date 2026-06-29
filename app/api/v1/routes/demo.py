from fastapi import APIRouter, Depends

from app.schemas.demo import DemoIngestionRequest, DemoIngestionResponse
from app.schemas.ingestion import IngestionRunStart
from app.schemas.topics import TopicProfileCreate
from app.services.ingestion_service import IngestionService, get_ingestion_service
from app.services.topic_service import TopicService, get_topic_service

router = APIRouter()


@router.post("/sample-ingestion", response_model=DemoIngestionResponse, status_code=201)
async def run_sample_ingestion(
    payload: DemoIngestionRequest,
    topic_service: TopicService = Depends(get_topic_service),
    ingestion_service: IngestionService = Depends(get_ingestion_service),
) -> DemoIngestionResponse:
    topic = await topic_service.create_topic(
        TopicProfileCreate(
            name=payload.name,
            research_idea=payload.research_idea,
            keywords=payload.keywords,
        )
    )
    ingestion_run = await ingestion_service.start_run(
        topic.id,
        IngestionRunStart(source_limit=payload.source_limit),
    )
    return DemoIngestionResponse(topic=topic, ingestion_run=ingestion_run)
