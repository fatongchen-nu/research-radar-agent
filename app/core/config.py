from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Research Radar Agent"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/research_radar"
    redis_url: str = "redis://localhost:6379/0"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    arxiv_max_results: int = Field(default=20, ge=1, le=100)
    semantic_scholar_api_key: str | None = None
    scheduler_enabled: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
