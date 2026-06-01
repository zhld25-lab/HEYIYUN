from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import auth, dashboard, projects, system, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(projects.router)
api_router.include_router(dashboard.router)
api_router.include_router(system.router)
