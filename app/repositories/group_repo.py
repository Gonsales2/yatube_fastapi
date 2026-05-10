from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.group import Group
from app.repositories.base import BaseRepositoryAsync


class GroupRepository(BaseRepositoryAsync[Group]):
    def __init__(self, db: AsyncSession):
        super().__init__(Group, db)

    async def get_by_slug(self, slug: str):
        try:
            stmt = select(Group).filter(Group.slug == slug)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            raise DatabaseConnectionError() from e
