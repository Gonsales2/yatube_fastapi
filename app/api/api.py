"""API router configuration for YaTube application."""

from fastapi import APIRouter

from app.api.v1 import auth
from app.api.v1 import comments
from app.api.v1 import groups
from app.api.v1 import posts


api_router = APIRouter()

api_router.include_router(
    auth.router,
    tags=["auth"]
)

api_router.include_router(
    groups.router,
    tags=["groups"]
)

api_router.include_router(
    posts.router,
    tags=["posts"]
)

api_router.include_router(
    comments.router,
    tags=["comments"]
)
