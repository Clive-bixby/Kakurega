from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.core.database import create_session_factory
from app.core.storage import STORAGE_ROOT, ensure_storage_dirs


def build_lifespan(settings: Settings):
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        session_factory, engine = create_session_factory(settings)
        app.state.settings = settings
        app.state.engine = engine
        app.state.session_factory = session_factory
        yield
        engine.dispose()

    return lifespan


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=build_lifespan(settings),
    )
    app.state.settings = settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    ensure_storage_dirs()
    app.mount("/storage", StaticFiles(directory=STORAGE_ROOT), name="storage")

    return app


app = create_app()
