from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.repositories.user_repo import UserRepository
from app.schemas.auth import Token, UserAuth, UserRegister
from datetime import datetime, timedelta
from jose import jwt
from app.config import settings

router = APIRouter()

@router.post("/api-token-auth/", response_model=Token)
def obtain_auth_token(
    credentials: UserAuth,
    db: Session = Depends(get_db)
):
    """
    Получить токен аутентификации.
    Принимает username/password в JSON-теле запроса,
    возвращает JWT-токен для заголовка `Authorization: Bearer <token>`.
    """
    repo = UserRepository(db)
    user = repo.get_by_username(credentials.username)
    
    if not user or not repo.verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": user.username}
    if access_token_expires:
        to_encode.update({"exp": datetime.utcnow() + access_token_expires})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return Token(token=encoded_jwt)

@router.post("/register/", status_code=status.HTTP_201_CREATED)
def register_user(
    user_in: UserRegister,
    db: Session = Depends(get_db)
):
    """Зарегистрировать нового пользователя."""
    repo = UserRepository(db)
    
    if repo.get_by_username(user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует",
        )
    
    if user_in.email and repo.get_by_email(user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже зарегистрирован",
        )
    
    user = repo.create_user(
        username=user_in.username,
        email=user_in.email,
        password=user_in.password,
    )
    
    return {"id": user.id, "username": user.username, "email": user.email}
