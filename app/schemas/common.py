from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class HealthResponse(BaseModel):
    status: str


class ListResponse(BaseModel, Generic[T]):
    data: list[T]
    has_more: bool = False


class Citation(BaseModel):
    paper_title: str
    url: str | None = None
    claim_id: str | None = None
    quote: str
    confidence: float = Field(default=0.5, ge=0, le=1)
