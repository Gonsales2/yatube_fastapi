from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.repositories.base import BaseRepositoryAsync
from app.exceptions import DatabaseIntegrityError, ConflictException, ValidationError
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRepository(BaseRepositoryAsync[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_username(self, username: str) -> Optional[User]:
        try:
            stmt = select(User).where(User.username == username)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            raise DatabaseIntegrityError(constraint=str(e)) from e

    async def get_by_email(self, email: str) -> Optional[User]:
        try:
            stmt = select(User).where(User.email == email)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            raise DatabaseIntegrityError(constraint=str(e)) from e

    async def create_user(self, username: str, email: str, password: str) -> User:
        password_bytes = password.encode("utf-8")
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
            password = password_bytes.decode("utf-8", errors="ignore")

        try:
            hashed_password = pwd_context.hash(password)
        except ValueError as e:
            if "cannot be longer than 72 bytes" in str(e):
                raise ValidationError(
                    field="password",
                    message="Пароль превышает техническое ограничение в 72 байта",
                ) from e
            raise

        try:
            user = await self.create(
                {"username": username, "email": email, "password": hashed_password}
            )
            return user
        except DatabaseIntegrityError as e:
            if e.constraint:
                if "username" in e.constraint.lower():
                    raise ConflictException(
                        resource_type="Пользователь", field="username", value=username
                    ) from e
                elif "email" in e.constraint.lower():
                    raise ConflictException(
                        resource_type="Пользователь", field="email", value=email
                    ) from e
            raise

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
