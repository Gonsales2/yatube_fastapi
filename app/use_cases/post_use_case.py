from app.repositories.post_repo import PostRepository
from app.repositories.group_repo import GroupRepository
from app.schemas.post import PostCreate, PostUpdate
from typing import List
from app.exceptions import (
    NotFoundException,
    PermissionDeniedException,
    ValidationError,
)
from app.models.user import User


class PostUseCase:
    def __init__(self, post_repo: PostRepository, group_repo: GroupRepository):
        self.post_repo = post_repo
        self.group_repo = group_repo

    async def get_posts(self, skip: int = 0, limit: int = 100) -> List[dict]:
        posts = await self.post_repo.get_all(skip, limit)
        return [self._serialize_post(p) for p in posts]

    async def get_post(self, post_id: int) -> dict:
        post = await self.post_repo.get(post_id)
        if not post:
            raise NotFoundException(resource_type="Пост", resource_id=post_id)
        return self._serialize_post(post)

    async def delete_post(self, user: User, post_id: int) -> None:
        post = await self.post_repo.get(post_id)
        if not post:
            raise NotFoundException(resource_type="Пост", resource_id=post_id)
        if not self.post_repo.can_modify(post, user.id):
            raise PermissionDeniedException(action="Удаление", resource_type="поста")
        await self.post_repo.delete(post)

    async def create_post(self, user: User, post_in: PostCreate) -> dict:
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
        create_data["author_id"] = user.id

        post = await self.post_repo.create(create_data)
        return self._serialize_post(post)

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

        if post_in.group is not None:
            group = await self.group_repo.get(post_in.group)
            if not group:
                raise ValidationError(
                    field="group", message=f"Группа с id={post_in.group} не существует"
                )

        update_data = post_in.model_dump(exclude_unset=True)
        updated_post = await self.post_repo.update(post, update_data)
        return self._serialize_post(updated_post)

    @staticmethod
    def _serialize_post(post) -> dict:
        return {
            "id": post.id,
            "author": post.author.username if post.author else None,
            "text": post.text,
            "pub_date": post.pub_date,
            "image": post.image,
            "group": post.group_id,
        }
