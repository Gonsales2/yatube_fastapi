from typing import List
from fastapi import APIRouter, Depends, Path, status, UploadFile, File
from app.api.deps import get_current_user
from app.models.user import User
from app.use_cases.post_image_use_case import PostImageUseCase  # Новый UseCase
from app.api.exception_handler import domain_to_http_exception
from app.exceptions import AppException
from dishka.integrations.fastapi import inject, FromDishka

router = APIRouter()


@router.post(
    "/{post_id}/images/",
    status_code=status.HTTP_201_CREATED,
)
@inject
async def add_images_to_post(
    post_id: int = Path(..., ge=1),
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    use_case: FromDishka[PostImageUseCase] = None,
):
    return await use_case.add_images_to_post(
        user=current_user,
        post_id=post_id,
        files=files,
    )


@router.delete("/{post_id}/images/", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_images_from_post(
    post_id: int = Path(..., ge=1),
    image_ids: List[int] = None,
    current_user: User = Depends(get_current_user),
    use_case: FromDishka[PostImageUseCase] = None,
):
    try:
        await use_case.delete_images_from_post(
            user=current_user, post_id=post_id, image_ids=image_ids
        )
        return None
    except AppException as e:
        raise domain_to_http_exception(e)
