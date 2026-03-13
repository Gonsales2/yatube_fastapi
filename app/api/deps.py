"""Dependencies for FastAPI application."""

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.user_repo import UserRepository


oauth2_scheme = APIKeyHeader(name="Authorization", auto_error=False)


def get_current_user(
    token: str = Security(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get current user from authentication token.

    Args:
        token: Authentication token from Authorization header
        db: Database session

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима аутентификация",
            headers={"WWW-Authenticate": "Token"},
        )

    if token.startswith("Token "):
        token = token.replace("Token ", "", 1)

    repo = UserRepository(db)
    user = repo.get_by_username(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен"
        )

    return user
