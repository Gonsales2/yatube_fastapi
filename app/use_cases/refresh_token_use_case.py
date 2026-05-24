from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.repositories.refresh_token_repo import RefreshTokenRepository
from app.repositories.user_repo import UserRepository
from app.config import settings
from app.exceptions import InvalidTokenException


class RefreshTokenUseCase:
    def __init__(self, refresh_repo, user_repo, jwt_service):
        self.refresh_repo = refresh_repo
        self.user_repo = user_repo
        self.jwt_service = jwt_service

    async def create_tokens(self, username: str, user_id: int) -> dict:
        access_token = self.jwt_service.create_access_token(username)
        refresh_token = self.jwt_service.create_refresh_token()
        await self.refresh_repo.create(
            {
                "user_id": user_id,
                "token": refresh_token,
                "expires_at": datetime.utcnow() + timedelta(days=30),
            }
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def refresh(self, refresh_token: str) -> dict:
        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            if payload.get("type") != "refresh":
                raise InvalidTokenException(detail="Неверный тип токена")
            username = payload.get("sub")
            if not username:
                raise InvalidTokenException()
        except JWTError:
            raise InvalidTokenException()

        stored = await self.refresh_repo.get_by_token(refresh_token)
        if not stored or stored.expires_at < datetime.utcnow():
            raise InvalidTokenException(detail="Refresh токен истёк или отозван")

        await self.refresh_repo.revoke_by_token(refresh_token)
        return await self.create_tokens(username, stored.user_id)

    async def logout(self, refresh_token: str) -> None:
        await self.refresh_repo.revoke_by_token(refresh_token)

    async def logout_all(self, user_id: int) -> None:
        await self.refresh_repo.revoke_all_for_user(user_id)
