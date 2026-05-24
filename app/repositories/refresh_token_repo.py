from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from datetime import datetime
from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepositoryAsync


class RefreshTokenRepository(BaseRepositoryAsync[RefreshToken]):
    def __init__(self, db: AsyncSession):
        super().__init__(RefreshToken, db)

    async def get_by_token(self, token: str):
        stmt = select(RefreshToken).where(
            RefreshToken.token == token,
            RefreshToken.is_revoked == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke_by_token(self, token: str):
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.token == token)
            .values(is_revoked=True)
        )
        await self.db.execute(stmt)
        await self.db.flush()

    async def revoke_all_for_user(self, user_id: int):
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False,
            )
            .values(is_revoked=True)
        )
        await self.db.execute(stmt)
        await self.db.flush()

    async def cleanup_expired(self):
        stmt = delete(RefreshToken).where(RefreshToken.expires_at < datetime.utcnow())
        await self.db.execute(stmt)
        await self.db.flush()
