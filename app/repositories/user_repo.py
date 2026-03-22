from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.repositories.base import BaseRepository
from app.exceptions import DatabaseIntegrityError, ConflictException, ValidationError
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_username(self, username: str) -> User | None:
        try:
            return self.db.query(User).filter(User.username == username).first()
        except Exception as e:
            raise
    
    def get_by_email(self, email: str) -> User | None:
        try:
            return self.db.query(User).filter(User.email == email).first()
        except Exception as e:
            raise
    
    def create_user(self, username: str, email: str, password: str) -> User:
        """Создать пользователя с безопасным хешированием пароля."""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.warning(f"🔍 DEBUG create_user:")
        logger.warning(f"  username: {username!r}")
        logger.warning(f"  email: {email!r}")
        logger.warning(f"  password (raw): {password!r}")
        logger.warning(f"  password length: {len(password)} chars, {len(password.encode('utf-8'))} bytes")
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
            password = password_bytes.decode('utf-8', errors='ignore')

        try:
            hashed_password = pwd_context.hash(password)
        except ValueError as e:
            if "cannot be longer than 72 bytes" in str(e):
                raise ValidationError(
                    field="password",
                    message="Пароль превышает техническое ограничение в 72 байта"
                ) from e
            raise

        try:
            return self.create({
                "username": username,
                "email": email,
                "password": hashed_password
            })
        except DatabaseIntegrityError as e:
            if e.constraint:
                if 'username' in e.constraint.lower() or 'auth_user_username_key' in e.constraint:
                    raise ConflictException(
                        resource_type="Пользователь",
                        field="username", 
                        value=username
                    ) from e
                elif 'email' in e.constraint.lower() or 'auth_user_email_key' in e.constraint:
                    raise ConflictException(
                        resource_type="Пользователь",
                        field="email",
                        value=email
                    ) from e
            raise
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверить пароль против хеша."""
        return pwd_context.verify(plain_password, hashed_password)
