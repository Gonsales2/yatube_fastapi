from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.post_image import PostImage
from app.repositories.base import BaseRepositoryAsync


class PostImageRepository(BaseRepositoryAsync[PostImage]):
    def __init__(self, db: AsyncSession):
        super().__init__(PostImage, db)

    async def get_by_post(self, post_id: int):
        stmt = (
            select(PostImage)
            .where(PostImage.post_id == post_id)
            .order_by(PostImage.order)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_post(self, post_id: int):
        from sqlalchemy import delete

        stmt = delete(PostImage).where(PostImage.post_id == post_id)
        await self.db.execute(stmt)
        await self.db.flush()
