from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.deps import get_db, get_current_user
from app.repositories.group_repo import GroupRepository
from app.schemas.group import GroupResponse, GroupCreate
from app.models.user import User
from app.use_cases.group_use_case import GroupUseCase
from app.exceptions import AppException
from app.api.exception_handler import domain_to_http_exception
from dishka.integrations.fastapi import inject
from dishka.integrations.fastapi import FromDishka

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
)


@router.get("/", response_model=List[GroupResponse])
@inject
async def read_groups(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    use_case: FromDishka[GroupUseCase] = None,
):
    try:
        return await use_case.get_groups(skip=skip, limit=limit)
    except AppException as e:
        raise domain_to_http_exception(e)


@router.get("/{group_id}", response_model=GroupResponse)
@inject
async def read_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    use_case: FromDishka[GroupUseCase] = None,
):
    try:
        return await use_case.get_group(group_id=group_id)
    except AppException as e:
        raise domain_to_http_exception(e)


@router.post(
    "/",
    response_model=GroupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новую группу",
)
@inject
async def create_group(
    group_in: GroupCreate,
    current_user: User = Depends(get_current_user),
    use_case: FromDishka[GroupUseCase] = None,
):
    try:
        return await use_case.create_group(group_in)
    except AppException as e:
        raise domain_to_http_exception(e)
