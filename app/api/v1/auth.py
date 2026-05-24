from fastapi import APIRouter, status, Form, Depends

from dishka.integrations.fastapi import inject, FromDishka

from sqlalchemy.ext.asyncio import AsyncSession
from dishka.integrations.fastapi import inject
from dishka.integrations.fastapi import FromDishka
from app.api.deps import get_current_user, get_db
from app.use_cases.auth_use_case import AuthUseCase
from app.use_cases.refresh_token_use_case import RefreshTokenUseCase
from app.schemas.auth import (
    TokenPair,
    UserRegister,
    RefreshRequest,
)
from app.models.user import User
from app.exceptions import AppException
from app.api.exception_handler import domain_to_http_exception

router = APIRouter()


@router.post(
    "/register/",
    status_code=status.HTTP_201_CREATED,
)
@inject
async def register_user(
    user_in: UserRegister,
    use_case: FromDishka[AuthUseCase],
):
    try:
        return await use_case.register(user_in)
    except AppException as e:
        raise domain_to_http_exception(e)


@router.post("/api-token-auth/", response_model=TokenPair)
@inject
async def obtain_auth_token(
    username: str = Form(...),
    password: str = Form(...),
    auth_uc: FromDishka[AuthUseCase] = None,
    refresh_uc: FromDishka[RefreshTokenUseCase] = None,
):
    try:
        credentials = type(
            "UserAuth",
            (),
            {"username": username, "password": password},
        )()

        auth_data = await auth_uc.authenticate(credentials)

        return await refresh_uc.create_tokens(
            username=auth_data["username"],
            user_id=auth_data["user_id"],
        )
    except AppException as e:
        raise domain_to_http_exception(e)


@router.post("/token/refresh/", response_model=TokenPair)
@inject
async def refresh_token(
    data: RefreshRequest,
    refresh_uc: FromDishka[RefreshTokenUseCase],
):
    try:
        return await refresh_uc.refresh(data.refresh_token)
    except AppException as e:
        raise domain_to_http_exception(e)


@router.post("/logout/", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def logout(
    data: RefreshRequest,
    refresh_uc: FromDishka[RefreshTokenUseCase],
):
    try:
        await refresh_uc.logout(data.refresh_token)
        return None
    except AppException as e:
        raise domain_to_http_exception(e)


@router.post("/logout-all/", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def logout_all(
    refresh_uc: FromDishka[RefreshTokenUseCase],
    current_user: User = Depends(get_current_user),
):
    try:
        await refresh_uc.logout_all(current_user.id)
        return None
    except AppException as e:
        raise domain_to_http_exception(e)
