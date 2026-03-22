from app.repositories.user_repo import UserRepository
from app.schemas.auth import UserAuth, UserRegister
from app.exceptions import (
    InvalidCredentialsException,
    ConflictException,
    ValidationError,
)


class AuthUseCase:
    """
    Бизнес-логика аутентификации.
    Отвечает за:
    - Валидацию учётных данных
    - Проверку уникальности username/email
    - Обогащение ошибок инфраструктурного слоя бизнес-контекстом
    """
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def authenticate(self, credentials: UserAuth) -> dict:
        """
        Аутентифицировать пользователя.
        Returns:
            dict с данными пользователя для создания токена
        Raises:
            InvalidCredentialsException: если username/password неверны
        """
        user = self.user_repo.get_by_username(credentials.username)
        
        if not user:
            raise InvalidCredentialsException()
        
        if not self.user_repo.verify_password(credentials.password, user.password):
            raise InvalidCredentialsException()

        return {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
        }
    
    def register(self, user_in: UserRegister) -> dict:
        """
        Зарегистрировать нового пользователя.
        Returns:
            dict с данными созданного пользователя 
        Raises:
            ConflictException: если username или email уже заняты
            ValidationError: если данные не проходят бизнес-валидацию
        """
        existing = self.user_repo.get_by_username(user_in.username)
        if existing:
            raise ConflictException(
                resource_type="Пользователь",
                field="username",
                value=user_in.username
            )
        
        if user_in.email:
            existing_email = self.user_repo.get_by_email(user_in.email)
            if existing_email:
                raise ConflictException(
                    resource_type="Пользователь", 
                    field="email",
                    value=user_in.email
                )

        forbidden_names = {"admin", "administrator", "root", "support"}
        if user_in.username.lower() in forbidden_names:
            raise ValidationError(
                field="username",
                message="Это имя пользователя зарезервировано"
            )

        user = self.user_repo.create_user(
            username=user_in.username,
            email=user_in.email,
            password=user_in.password,
        )
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
