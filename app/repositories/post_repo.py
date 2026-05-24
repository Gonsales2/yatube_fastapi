from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.post import Post
from app.repositories.base import BaseRepositoryAsync
from app.exceptions import (
    DatabaseIntegrityError,
    DatabaseConnectionError,
    ConflictException,
)


class PostRepository(BaseRepositoryAsync[Post]):
    def __init__(self, db: AsyncSession):
        super().__init__(Post, db)

    async def get_with_images(self, post_id: int) -> Post | None:
        stmt = (
            select(Post)
            .options(selectinload(Post.images))
            .options(selectinload(Post.author))
            .where(Post.id == post_id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_with_images(self, skip: int = 0, limit: int = 100) -> list[Post]:
        stmt = (
            select(Post)
            .options(selectinload(Post.images))
            .options(selectinload(Post.author))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create(self, obj_create: dict):
        try:
            return await super().create(obj_create)
        except DatabaseIntegrityError as e:
            if e.constraint and "group_id" in e.constraint.lower():
                raise ConflictException(
                    resource_type="Пост",
                    field="group",
                    value=obj_create.get("group_id"),
                ) from e
            raise

    async def get_by_author(self, author_id: int, skip: int = 0, limit: int = 100):
        try:
            stmt = (
                select(Post)
                .filter(Post.author_id == author_id)
                .offset(skip)
                .limit(limit)
            )
            result = await self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise DatabaseIntegrityError() from e

    async def get_by_group(self, group_id: int, skip: int = 0, limit: int = 100):
        try:
            stmt = (
                select(Post).filter(Post.group_id == group_id).offset(skip).limit(limit)
            )
            result = await self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise DatabaseIntegrityError() from e

    def can_modify(self, post: Post, user_id: int) -> bool:
        return post.author_id == user_id
