from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings

logger = logging.getLogger("erp")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialise database tables and seed data on startup (best-effort for dev).
    try:
        from app.db.init_db import init

        init()
        logger.info("Database initialised and seeded.")
    except Exception as exc:  # pragma: no cover - startup resilience
        logger.warning("Database init skipped: %s", exc)
    yield


app = FastAPI(
    title=settings.APP_NAME_EN,
    description=settings.APP_NAME_CN,
    version="1.0.0",
    lifespan=lifespan,
)

_origins = settings.cors_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_origin_regex=r"https://.*\.streamlit\.app" if "*" not in _origins else None,
    allow_credentials="*" not in _origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.APP_NAME_EN}
