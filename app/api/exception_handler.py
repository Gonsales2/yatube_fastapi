from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.exceptions import AppException, AuthenticationException
import logging

logger = logging.getLogger(__name__)


async def app_exception_handler(request: Request, exc: AppException):
    """
    Обработчик кастомных исключений приложения.
    Конвертирует AppException в JSON-ответ с правильным статус-кодом.
    """
    logger.warning(
        f"AppException: {exc.detail} | "
        f"path={request.url.path} | "
        f"method={request.method} | "
        f"context={getattr(exc, 'context', {})}"
    )
    if exc.status_code == status.HTTP_204_NO_CONTENT:
        return Response(status_code=204, headers=getattr(exc, 'headers', None))
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=getattr(exc, 'headers', None),
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Переопределённый обработчик HTTPException для единообразного формата.
    """
    logger.warning(f"HTTPException: {exc.detail} | path={request.url.path}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=getattr(exc, 'headers', None),
    )

def domain_to_http_exception(exc: AppException) -> HTTPException:
    """Конвертировать AppException в FastAPI HTTPException."""
    return HTTPException(
        status_code=exc.status_code,
        detail=exc.detail,
        headers=getattr(exc, 'headers', None),
    )
