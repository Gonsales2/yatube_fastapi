from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories.user_repo import UserRepository
from app.schemas.auth import Token, UserAuth 

router = APIRouter()


@router.post("/api-token-auth/", response_model=Token)
def obtain_auth_token(
    credentials: UserAuth, 
    db: Session = Depends(get_db)
):
    """
    Получить токен аутентификации.
    
    Принимает username/password в JSON-теле запроса,
    возвращает токен для заголовка `Authorization: Token <token>`.
    """
    repo = UserRepository(db)
    user = repo.get_by_username(credentials.username)
    
    if not user or not repo.verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Token"},
        )
    
    return Token(token=user.username)
