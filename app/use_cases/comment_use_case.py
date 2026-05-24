from app.repositories.comment_repo import CommentRepository
from app.repositories.post_repo import PostRepository
from app.repositories.comment_image_repo import CommentImageRepository
from app.schemas.comment import CommentCreate, CommentUpdate
from app.exceptions import (
    NotFoundException,
    PermissionDeniedException,
    ValidationError,
)
from app.models.user import User
from fastapi import UploadFile, File

class CommentUseCase:
    def __init__(
        self,
        comment_repo: CommentRepository,
        post_repo: PostRepository,
        image_repo: CommentImageRepository,
    ):
        self.comment_repo = comment_repo
        self.post_repo = post_repo
        self.image_repo = image_repo

    async def get_comments(self, post_id: int, skip: int = 0, limit: int = 100) -> list:
        if not await self.post_repo.get(post_id):
            raise NotFoundException(resource_type="Пост", resource_id=post_id)

        comments = await self.comment_repo.get_by_post_with_relations(
            post_id, skip, limit
        )
        return [self._serialize(c) for c in comments]

    async def get_comment(self, post_id: int, comment_id: int) -> dict:
        if not await self.post_repo.get(post_id):
            raise NotFoundException(resource_type="Пост", resource_id=post_id)

        comment = await self.comment_repo.get_with_relations(comment_id)
        if not comment or comment.post_id != post_id:
            raise NotFoundException(resource_type="Комментарий", resource_id=comment_id)

        return self._serialize(comment)

    async def create_comment(
        self,
        user: User,
        post_id: int,
        comment_in: CommentCreate,
        image_paths: list[str] | None = None,
    ) -> dict:
        if not await self.post_repo.get(post_id):
            raise NotFoundException(resource_type="Пост", resource_id=post_id)

        if len(comment_in.text.strip()) < 2:
            raise ValidationError(
                field="text", message="Комментарий должен содержать минимум 2 символа"
            )

        create_data = comment_in.model_dump()
        create_data.update({"author_id": user.id, "post_id": post_id})

        comment = await self.comment_repo.create(create_data)
        if image_paths:
            if len(image_paths) > 5:
                raise ValidationError(field="image", message="Максимум 5 картинок")
            await self.image_repo.add_many(comment.id, image_paths)

        comment_with_relations = await self.comment_repo.get_with_relations(comment.id)
        return self._serialize(comment_with_relations)

    async def update_comment(
        self,
        user: User,
        post_id: int,
        comment_id: int,
        comment_in: CommentUpdate,
        full_update: bool = False,
    ) -> dict:
        comment = await self.comment_repo.get(comment_id)
        if not comment or comment.post_id != post_id:
            raise NotFoundException(resource_type="Комментарий", resource_id=comment_id)

        if not self.comment_repo.can_modify(comment, user.id):
            raise PermissionDeniedException(
                action="Редактирование", resource_type="комментария"
            )

        if full_update and comment_in.text and not comment_in.text.strip():
            raise ValidationError(
                field="text", message="Текст обязателен для полного обновления"
            )

        update_data = comment_in.model_dump(exclude_unset=True)
        updated = await self.comment_repo.update(comment, update_data)

        updated_with_relations = await self.comment_repo.get_with_relations(updated.id)
        return self._serialize(updated_with_relations)

    async def delete_comment(self, user: User, post_id: int, comment_id: int) -> None:
        comment = await self.comment_repo.get(comment_id)
        if not comment or comment.post_id != post_id:
            raise NotFoundException(resource_type="Комментарий", resource_id=comment_id)

        if not self.comment_repo.can_modify(comment, user.id):
            raise PermissionDeniedException(
                action="Удаление", resource_type="комментария"
            )

        await self.comment_repo.delete(comment)

    async def add_images_to_comment(
        self,
        user: User,
        post_id: int,
        comment_id: int,
        files: List[UploadFile],
    ) -> dict:
        from app.api.v1.upload import save_image, validate_image
        if not await self.post_repo.get(post_id):
            raise NotFoundException(resource_type="Пост", resource_id=post_id)

        comment = await self.comment_repo.get(comment_id)
        if not comment or comment.post_id != post_id:
            raise NotFoundException(resource_type="Комментарий", resource_id=comment_id)

        if not self.comment_repo.can_modify(comment, user.id):
            raise PermissionDeniedException(
                action="Добавление изображений", resource_type="комментария"
            )

        if not files:
            raise ValidationError(field="files", message="Не выбрано ни одного файла")
        if len(files) > 5:
            raise ValidationError(field="files", message="Максимум 5 изображений")

        existing = await self.image_repo.get_by_comment(comment_id)
        next_order = len(existing)
        

        image_paths = []
        for idx, file in enumerate(files):
            validate_image(file)
            path = await save_image(file, "comments")
            image_paths.append(path)
        

        await self.image_repo.add_many(comment_id, image_paths)

        comment_with_images = await self.comment_repo.get_with_relations(comment_id)
        return self._serialize(comment_with_images)
    
    async def add_image_to_comment(
        self,
        user: User,
        post_id: int,
        comment_id: int,
        file: UploadFile,
    ) -> dict:
        from app.api.v1.upload import save_image, validate_image
        

        if not await self.post_repo.get(post_id):
            raise NotFoundException(resource_type="Пост", resource_id=post_id)
        
        comment = await self.comment_repo.get(comment_id)
        if not comment or comment.post_id != post_id:
            raise NotFoundException(resource_type="Комментарий", resource_id=comment_id)
        

        if not self.comment_repo.can_modify(comment, user.id):
            raise PermissionDeniedException(
                action="Добавление изображения", resource_type="комментария"
            )
  
        existing = await self.image_repo.get_by_comment(comment_id)
        if existing:
            raise ValidationError(
                field="file",
                message="К комментарию уже добавлено изображение. Разрешено только одно.",
            )

        validate_image(file)
        image_path = await save_image(file, "comments")

        await self.image_repo.create({
            "image": image_path,
            "order": 0,
            "comment_id": comment_id,
        })
        
        comment_with_image = await self.comment_repo.get_with_relations(comment_id)
        return self._serialize(comment_with_image)
    

    @staticmethod
    def _serialize(comment) -> dict:
        author_name = comment.author.username if comment.author else "unknown"
        image = []

        if hasattr(comment, "image") and comment.image:
            image = [
                {
                    "id": img.id,
                    "image": img.image,
                    "order": img.order,
                    "url": f"/media/{img.image}",
                }
                for img in sorted(comment.image, key=lambda i: i.order)
            ]

        return {
            "id": comment.id,
            "author": author_name,
            "text": comment.text,
            "created": comment.created,
            "post": comment.post_id,
            "image": image,
        }
