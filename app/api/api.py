from fastapi import APIRouter

from app.api.v1 import auth, comments, groups, posts, upload

api_router = APIRouter()

api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(groups.router, tags=["groups"])
api_router.include_router(posts.router, tags=["posts"])
api_router.include_router(comments.router, tags=["comments"])
api_router.include_router(upload.router, tags=["upload"])
