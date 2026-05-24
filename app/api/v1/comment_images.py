from typing import List

from fastapi import (
    APIRouter,
    Depends,
    File,
    Path,
    UploadFile,
    status,
)

from dishka.integrations.fastapi import (
    FromDishka,
    inject,
)

from app.api.deps import get_current_user
from app.models.user import User
from app.use_cases.comment_image_use_case import CommentImageUseCase

router = APIRouter(
    tags=["Comment Images"],
)


@router.post(
    "/posts/{post_id}/comments/{comment_id}/images/",
    status_code=status.HTTP_201_CREATED,
    summary="Добавить картинки к комментарию",
)
@inject
async def add_images_to_comment(
    post_id: int = Path(..., ge=1),
    comment_id: int = Path(..., ge=1),
    files: List[UploadFile] = File(
        ...,
        description="Список изображений (максимум 10)",
    ),
    current_user: User = Depends(get_current_user),
    use_case: FromDishka[CommentImageUseCase] = None,
):
    return await use_case.add_images_to_comment(
        user=current_user,
        post_id=post_id,
        comment_id=comment_id,
        files=files,
    )


@router.delete(
    "/posts/{post_id}/comments/{comment_id}/images/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить картинки комментария",
)
@inject
async def delete_images_from_comment(
    post_id: int = Path(..., ge=1),
    comment_id: int = Path(..., ge=1),
    image_ids: List[int] | None = None,
    current_user: User = Depends(get_current_user),
    use_case: FromDishka[CommentImageUseCase] = None,
):
    await use_case.delete_images_from_comment(
        user=current_user,
        post_id=post_id,
        comment_id=comment_id,
        image_ids=image_ids,
    )

    return None
