import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.api import api_router
from app.config import settings
from fastapi.exceptions import HTTPException
from app.api.exception_handler import app_exception_handler, http_exception_handler
from app.exceptions import AppException
from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from app.di.container import container

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("yatube")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

setup_dishka(container, app)


app.mount("/media", StaticFiles(directory=settings.MEDIA_ROOT), name="media")

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_user_actions(request: Request, call_next):
    if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)

    start_time = time.time()
    client_host = request.client.host if request.client else "unknown"
    method = request.method
    path = request.url.path

    response = await call_next(request)
    process_time = time.time() - start_time

    logger.info(
        f"Action: {method} {path} | "
        f"Client: {client_host} | "
        f"Status: {response.status_code} | "
        f"Duration: {process_time:.3f}s"
    )

    return response


app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("shutdown")
async def shutdown_event():
    await container.close()


@app.get("/")
async def root() -> dict:
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
