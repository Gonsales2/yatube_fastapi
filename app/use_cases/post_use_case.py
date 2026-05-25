from fastapi import UploadFile, File
from app.repositories.post_repo import PostRepository
from app.repositories.group_repo import GroupRepository
from app.repositories.post_image_repo import PostImageRepository
from app.api.v1.upload import save_image, validate_image
from app.schemas.post import PostCreate, PostUpdate
from typing import List
from app.exceptions import (
    NotFoundException,
    PermissionDeniedException,
    ValidationError,
)
from app.models.user import User


class PostUseCase:
    def __init__(
        self,
        post_repo: PostRepository,
        group_repo: GroupRepository,
        image_repo: PostImageRepository,
    ):
        self.post_repo = post_repo
        self.group_repo = group_repo
        self.image_repo = image_repo

    async def get_post(self, post_id: int) -> dict:
        post = await self.post_repo.get_with_images(post_id)
        if not post:
            raise NotFoundException(resource_type="Пост", resource_id=post_id)
        return self._serialize_post(post)

    async def get_posts(self, skip: int = 0, limit: int = 100) -> List[dict]:
        posts = await self.post_repo.get_all_with_images(skip, limit)
        return [self._serialize_post(p) for p in posts]

    async def delete_post(self, user: User, post_id: int) -> None:
        post = await self.post_repo.get(post_id)
        if not post:
            raise NotFoundException(resource_type="Пост", resource_id=post_id)
        if not self.post_repo.can_modify(post, user.id):
            raise PermissionDeniedException(action="Удаление", resource_type="поста")
        await self.post_repo.delete(post)

    async def create_post(
        self, user: User, post_in: PostCreate, image_paths: list[str] | None = None
    ) -> dict:
        if post_in.group is not None:
            group = await self.group_repo.get(post_in.group)
            if not group:
                raise ValidationError(
                    field="group", message=f"Группа с id={post_in.group} не существует"
                )

        if len(post_in.text.strip()) < 3:
            raise ValidationError(
                field="text", message="Текст поста должен содержать минимум 3 символа"
            )

        create_data = post_in.model_dump()
        if create_data.get("group") is not None:
            create_data["group_id"] = create_data.pop("group")
        create_data["author_id"] = user.id

        post = await self.post_repo.create(create_data)

        if image_paths:
            for idx, path in enumerate(image_paths):
                await self.image_repo.create(
                    {
                        "image": path,
                        "order": idx,
                        "post_id": post.id,
                    }
                )
        post_with_images = await self.post_repo.get_with_images(post.id)
        return self._serialize_post(post_with_images)

    async def update_post(
        self, user: User, post_id: int, post_in: PostUpdate, full_update: bool = False
    ) -> dict:
        post = await self.post_repo.get(post_id)
        if not post:
            raise NotFoundException(resource_type="Пост", resource_id=post_id)

        if not self.post_repo.can_modify(post, user.id):
            raise PermissionDeniedException(
                action="Редактирование", resource_type="поста"
            )

        if full_update and post_in.text is not None and not post_in.text.strip():
            raise ValidationError(
                field="text", message="Поле text обязательно для полного обновления"
            )

        update_data = post_in.model_dump(exclude_unset=True)
        if update_data.get("group") is not None:
            group = await self.group_repo.get(update_data["group"])
            if not group:
                raise ValidationError(
                    field="group",
                    message=f"Группа с id={update_data['group']} не существует",
                )
            update_data["group_id"] = update_data.pop("group")

        updated_post = await self.post_repo.update(post, update_data)
        updated_with_images = await self.post_repo.get_with_images(updated_post.id)
        return self._serialize_post(updated_with_images)

    async def add_images_to_post(
        self,
        user: User,
        post_id: int,
        files: List[UploadFile],
    ) -> dict:

        post = await self.post_repo.get(post_id)
        if not post:
            raise NotFoundException(resource_type="Пост", resource_id=post_id)

        if not self.post_repo.can_modify(post, user.id):
            raise PermissionDeniedException(
                action="Добавление изображений", resource_type="поста"
            )

        if not files:
            raise ValidationError(field="files", message="Не выбрано ни одного файла")
        if len(files) > 10:
            raise ValidationError(field="files", message="Максимум 10 изображений")

        existing = await self.image_repo.get_by_post(post_id)
        next_order = len(existing)

        for idx, file in enumerate(files):
            validate_image(file)
            image_path = await save_image(file, "posts")

            await self.image_repo.create(
                {
                    "image": image_path,
                    "order": next_order + idx,
                    "post_id": post_id,
                }
            )

        post_with_images = await self.post_repo.get_with_images(post_id)
        return self._serialize_post(post_with_images)

    async def add_image_to_post(
        self,
        user: User,
        post_id: int,
        file: UploadFile,
    ) -> dict:
        from app.api.v1.upload import save_image, validate_image

        post = await self.post_repo.get(post_id)
        if not post:
            raise NotFoundException(resource_type="Пост", resource_id=post_id)

        if not self.post_repo.can_modify(post, user.id):
            raise PermissionDeniedException(
                action="Добавление изображения", resource_type="поста"
            )

        existing = await self.image_repo.get_by_post(post_id)
        if existing:
            raise ValidationError(
                field="file",
                message="К посту уже добавлено изображение. Разрешено только одно.",
            )

        validate_image(file)
        image_path = await save_image(file, "posts")

        await self.image_repo.create(
            {
                "image": image_path,
                "order": 0,
                "post_id": post_id,
            }
        )

        post_with_image = await self.post_repo.get_with_images(post_id)
        return self._serialize_post(post_with_image)

    @staticmethod
    def _serialize_post(post) -> dict:
        author_name = post.author.username if post.author else None
        images = (
            [
                {
                    "id": img.id,
                    "image": img.image,
                    "order": img.order,
                    "url": f"/media/{img.image}",
                }
                for img in sorted(post.images, key=lambda i: i.order)
            ]
            if post.images
            else []
        )

        return {
            "id": post.id,
            "author": author_name,
            "text": post.text,
            "pub_date": post.pub_date,
            "images": images,
            "group": post.group_id,
        }
