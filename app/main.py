from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.config import settings
from fastapi.exceptions import HTTPException
from app.api.exception_handler import app_exception_handler, http_exception_handler
from app.exceptions import AppException
from fastapi.security import OAuth2PasswordBearer


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/api-token-auth/")

@app.get("/")
def root() -> dict:
    """Root endpoint returning welcome message."""
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
