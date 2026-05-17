from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.comment import Comment
from app.repositories.base import BaseRepositoryAsync
from app.exceptions import DatabaseIntegrityError, DatabaseConnectionError


class CommentRepository(BaseRepositoryAsync[Comment]):
    def __init__(self, db: AsyncSession):
        super().__init__(Comment, db)

    def can_modify(self, comment: Comment, user_id: int) -> bool:
        return comment.author_id == user_id

    async def get_by_post(self, post_id: int, skip: int = 0, limit: int = 100):
        try:
            stmt = (
                select(Comment)
                .filter(Comment.post_id == post_id)
                .order_by(Comment.created)
                .offset(skip)
                .limit(limit)
            )
            result = await self.db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            raise DatabaseIntegrityError(constraint=str(e)) from e
