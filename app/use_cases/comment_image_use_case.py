from typing import List

from fastapi import UploadFile

from app.models.user import User
from app.models.comment import Comment
from app.models.comment_image import CommentImage

from app.repositories.comment_repo import CommentRepository
from app.repositories.comment_image_repo import CommentImageRepository

from app.services.image_service import ImageService

from app.exceptions import (
    ForbiddenException,
    NotFoundException,
    ValidationException,
)

MAX_COMMENT_IMAGES = 10


class CommentImageUseCase:

    def __init__(
        self,
        comment_repo: CommentRepository,
        comment_image_repo: CommentImageRepository,
        image_service: ImageService,
    ):
        self.comment_repo = comment_repo
        self.comment_image_repo = comment_image_repo
        self.image_service = image_service

    async def add_images_to_comment(
        self,
        user: User,
        post_id: int,
        comment_id: int,
        files: List[UploadFile],
    ) -> list[dict]:

        comment = await self.comment_repo.get_by_id(comment_id)

        if not comment:
            raise NotFoundException(
                detail="Комментарий не найден",
            )

        if comment.post_id != post_id:
            raise ValidationException(
                detail="Комментарий не принадлежит посту",
            )

        if comment.author_id != user.id:
            raise ForbiddenException(
                detail="Нет прав на изменение комментария",
            )

        if len(files) > MAX_COMMENT_IMAGES:
            raise ValidationException(
                detail=f"Максимум {MAX_COMMENT_IMAGES} изображений",
            )

        results = []

        for file in files:

            self.image_service.validate_image(file)

            image_path = await self.image_service.save_image(
                file=file,
                subdirectory=f"comments/{comment_id}",
            )

            image = await self.comment_image_repo.create(
                comment_id=comment.id,
                image=image_path,
            )

            results.append(
                {
                    "id": image.id,
                    "path": image.image,
                    "url": f"/media/{image.image}",
                }
            )

        return results

    async def delete_images_from_comment(
        self,
        user: User,
        post_id: int,
        comment_id: int,
        image_ids: list[int] | None,
    ) -> None:

        comment = await self.comment_repo.get_by_id(comment_id)

        if not comment:
            raise NotFoundException(
                detail="Комментарий не найден",
            )

        if comment.post_id != post_id:
            raise ValidationException(
                detail="Комментарий не принадлежит посту",
            )

        if comment.author_id != user.id:
            raise ForbiddenException(
                detail="Нет прав на удаление изображений",
            )

        image = await self.comment_image_repo.get_many_by_ids(
            image_ids=image_ids,
            comment_id=comment.id,
        )

        for image in image:

            await self.image_service.delete_image(
                image.image,
            )

            await self.comment_image_repo.delete(
                image.id,
            )
