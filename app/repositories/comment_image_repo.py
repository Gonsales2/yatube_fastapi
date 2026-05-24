from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.comment_image import CommentImage
from app.repositories.base import BaseRepositoryAsync
from app.exceptions import DatabaseConnectionError, DatabaseIntegrityError


class CommentImageRepository(BaseRepositoryAsync[CommentImage]):
    def __init__(self, db: AsyncSession):
        super().__init__(CommentImage, db)

    async def get_by_comment(self, comment_id: int) -> List[CommentImage]:
        try:
            stmt = (
                select(CommentImage)
                .where(CommentImage.comment_id == comment_id)
                .order_by(CommentImage.order.asc())
            )
            result = await self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise DatabaseConnectionError() from e

    async def delete_by_comment(self, comment_id: int) -> None:
        try:
            stmt = delete(CommentImage).where(CommentImage.comment_id == comment_id)
            await self.db.execute(stmt)
            await self.db.flush()
        except Exception as e:
            raise DatabaseIntegrityError(constraint=str(e)) from e

    async def add_many(
        self, comment_id: int, image_paths: List[str]
    ) -> List[CommentImage]:
        if not image_paths:
            return []

        try:
            images = []
            for idx, path in enumerate(image_paths):
                image = CommentImage(
                    image=path,
                    order=idx,
                    comment_id=comment_id,
                )
                self.db.add(image)
                images.append(image)

            await self.db.flush()
            for img in images:
                await self.db.refresh(img)
            return images
        except Exception as e:
            await self.db.rollback()
            raise DatabaseIntegrityError(constraint=str(e)) from e

    async def get_count(self, comment_id: int) -> int:
        try:
            from sqlalchemy import func

            stmt = (
                select(func.count())
                .select_from(CommentImage)
                .where(CommentImage.comment_id == comment_id)
            )
            result = await self.db.execute(stmt)
            return result.scalar_one()
        except Exception as e:
            raise DatabaseConnectionError() from e
