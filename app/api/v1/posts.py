from fastapi import APIRouter, Depends, Path, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.repositories.post_repo import PostRepository
from app.repositories.group_repo import GroupRepository
from app.schemas.post import PostCreate, PostResponse, PostUpdate
from app.use_cases.post_use_case import PostUseCase
from app.exceptions import AppException
from app.api.exception_handler import domain_to_http_exception
from dishka.integrations.fastapi import inject
from dishka.integrations.fastapi import FromDishka

router = APIRouter()


@router.get("/", response_model=List[PostResponse])
@inject
async def read_posts(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    use_case: FromDishka[PostUseCase] = None,
):
    try:
        return await use_case.get_posts(skip=skip, limit=limit)

    except AppException as e:
        raise domain_to_http_exception(e)


@router.get("/group/{group_id}/post/{post_id}", response_model=PostResponse)
@inject
async def read_post(
    post_id: int = Path(..., ge=1),
    current_user: User = Depends(get_current_user),
    use_case: FromDishka[PostUseCase] = None,
):
    try:
        return await use_case.get_post(post_id=post_id)
    except AppException as e:
        raise domain_to_http_exception(e)


@router.post(
    "/group/{group_id}/post",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_post(
    post_in: PostCreate,
    current_user: User = Depends(get_current_user),
    use_case: FromDishka[PostUseCase] = None,
):
    try:
        return await use_case.create_post(user=current_user, post_in=post_in)
    except AppException as e:
        raise domain_to_http_exception(e)


@router.patch("/group/{group_id}/post/{post_id}", response_model=PostResponse)
@inject
async def update_post_partial(
    post_id: int = Path(..., ge=1),
    post_in: PostUpdate = None,
    current_user: User = Depends(get_current_user),
    use_case: FromDishka[PostUseCase] = None,
):
    try:
        return await use_case.update_post(
            user=current_user, post_id=post_id, post_in=post_in, full_update=False
        )
    except AppException as e:
        raise domain_to_http_exception(e)


@router.put("/group/{group_id}/post/{post_id}", response_model=PostResponse)
@inject
async def update_post_full(
    post_id: int = Path(..., ge=1),
    post_in: PostUpdate = None,
    current_user: User = Depends(get_current_user),
    use_case: FromDishka[PostUseCase] = None,
):
    try:
        return await use_case.update_post(
            user=current_user, post_id=post_id, post_in=post_in, full_update=True
        )
    except AppException as e:
        raise domain_to_http_exception(e)


@router.delete(
    "/group/{group_id}/post/{post_id}", status_code=status.HTTP_204_NO_CONTENT
)
@inject
async def delete_post(
    post_id: int = Path(..., ge=1),
    current_user: User = Depends(get_current_user),
    use_case: FromDishka[PostUseCase] = None,
):
    try:
        await use_case.delete_post(user=current_user, post_id=post_id)
        return None
    except AppException as e:
        raise domain_to_http_exception(e)


@router.post(
    "/group/{group_id}/post/{post_id}/images/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить изображения к посту",
)
@inject
async def add_images_to_post(
    post_id: int = Path(..., ge=1),
    file: UploadFile = File(..., description="Изображение"),
    current_user: User = Depends(get_current_user),
    use_case: FromDishka[PostUseCase] = None,
):
    try:
        return await use_case.add_image_to_post(
            user=current_user,
            post_id=post_id,
            file=file,
        )
    except AppException as e:
        raise domain_to_http_exception(e)
