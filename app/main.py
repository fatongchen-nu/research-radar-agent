from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import register_error_handlers


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0")
    register_error_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
