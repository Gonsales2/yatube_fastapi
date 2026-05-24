from typing import List
from fastapi import APIRouter, Depends, Path, status, UploadFile, File 
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.comment_repo import CommentRepository
from app.repositories.post_repo import PostRepository
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.use_cases.comment_use_case import CommentUseCase
from app.exceptions import AppException
from app.api.exception_handler import domain_to_http_exception
from dishka.integrations.fastapi import inject
from dishka.integrations.fastapi import FromDishka

router = APIRouter()


@router.get("/group/{group_id}/post/{post_id}/comment/", response_model=List[CommentResponse])
@inject
async def read_comments(
    post_id: int = Path(..., ge=1),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    use_case: FromDishka[CommentUseCase] = None,
):
    try:
        return await use_case.get_comments(post_id=post_id, skip=skip, limit=limit)
    except AppException as e:
        raise domain_to_http_exception(e)


@router.get("/group/{group_id}/post/{post_id}/comment/{comment_id}", response_model=CommentResponse)
@inject
async def read_comment(
    post_id: int = Path(..., ge=1),
    comment_id: int = Path(..., ge=1),
    current_user: User = Depends(get_current_user),
    use_case: FromDishka[CommentUseCase] = None,
):
    try:
        return await use_case.get_comment(post_id=post_id, comment_id=comment_id)
    except AppException as e:
        raise domain_to_http_exception(e)


@router.post(
    "/group/{group_id}/post/{post_id}/comment/",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def create_comment(
    post_id: int = Path(..., ge=1),
    comment_in: CommentCreate = None,
    current_user: User = Depends(get_current_user),
    use_case: FromDishka[CommentUseCase] = None,
):
    try:
        return await use_case.create_comment(
            user=current_user, post_id=post_id, comment_in=comment_in
        )
    except AppException as e:
        raise domain_to_http_exception(e)


@router.patch("/group/{group_id}/post/{post_id}/comment/{comment_id}", response_model=CommentResponse)
@inject
async def update_comment_partial(
    post_id: int = Path(..., ge=1),
    comment_id: int = Path(..., ge=1),
    comment_in: CommentUpdate = None,
    current_user: User = Depends(get_current_user),
    use_case: FromDishka[CommentUseCase] = None,
):
    try:
        return await use_case.update_comment(
            user=current_user,
            post_id=post_id,
            comment_id=comment_id,
            comment_in=comment_in,
            full_update=False,
        )
    except AppException as e:
        raise domain_to_http_exception(e)


@router.put("/group/{group_id}/post/{post_id}/comment/{comment_id}", response_model=CommentResponse)
@inject
async def update_comment_full(
    post_id: int = Path(..., ge=1),
    comment_id: int = Path(..., ge=1),
    comment_in: CommentUpdate = None,
    current_user: User = Depends(get_current_user),
    use_case: FromDishka[CommentUseCase] = None,
):
    try:
        return await use_case.update_comment(
            user=current_user,
            post_id=post_id,
            comment_id=comment_id,
            comment_in=comment_in,
            full_update=True,
        )
    except AppException as e:
        raise domain_to_http_exception(e)


@router.delete(
    "/group/{group_id}/post/{post_id}/comment/{comment_id}", status_code=status.HTTP_204_NO_CONTENT
)
@inject
async def delete_comment(
    post_id: int = Path(..., ge=1),
    comment_id: int = Path(..., ge=1),
    current_user: User = Depends(get_current_user),
    use_case: FromDishka[CommentUseCase] = None,
):
    try:
        await use_case.delete_comment(
            user=current_user, post_id=post_id, comment_id=comment_id
        )
        return None
    except AppException as e:
        raise domain_to_http_exception(e)

@router.post(
    "/group/{group_id}/post/{post_id}/comment/{comment_id}/image/",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Загрузить изображение к комментарию",
    description="К комментарию можно добавить 1 изображение",
)
@inject
async def add_image_to_comment(
    post_id: int = Path(..., ge=1),
    comment_id: int = Path(..., ge=1),
    file: UploadFile = File(..., description="Добавить изображение"),
    current_user: User = Depends(get_current_user),
    use_case: FromDishka[CommentUseCase] = None,
):
    try:
        return await use_case.add_image_to_comment(
            user=current_user,
            post_id=post_id,
            comment_id=comment_id,
            file=file,
        )
    except AppException as e:
        raise domain_to_http_exception(e)