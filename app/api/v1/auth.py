from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.repositories.user_repo import UserRepository
from app.use_cases.auth_use_case import AuthUseCase
from app.schemas.auth import Token, UserRegister
from fastapi import Form
from app.exceptions import AppException
from app.api.exception_handler import domain_to_http_exception
from datetime import datetime, timedelta
from jose import jwt
from app.config import settings

router = APIRouter()


@router.post("/api-token-auth/", response_model=Token)
async def obtain_auth_token(
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        repo = UserRepository(db)
        use_case = AuthUseCase(repo)

        credentials = type(
            "UserAuth", (), {"username": username, "password": password}
        )()
        auth_data = await use_case.authenticate(credentials)

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": auth_data["username"],
            "exp": datetime.utcnow() + access_token_expires,
        }

        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )

        return Token(access_token=encoded_jwt, token_type="bearer")

    except AppException as e:
        raise domain_to_http_exception(e)


@router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    try:
        repo = UserRepository(db)
        use_case = AuthUseCase(repo)

        result = await use_case.register(user_in)
        return result

    except AppException as e:
        raise domain_to_http_exception(e)
