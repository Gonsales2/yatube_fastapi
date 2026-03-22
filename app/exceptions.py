from typing import Optional, Dict, Any


class AppException(Exception):
    """Базовое исключение приложения."""
    status_code: int = 500
    detail: str = "Внутренняя ошибка сервера"
    headers: Optional[Dict[str, str]] = None
    
    def __init__(
        self, 
        detail: Optional[str] = None, 
        headers: Optional[Dict[str, str]] = None, 
        **context: Any
    ):
        if detail:
            self.detail = detail
        if headers:
            self.headers = headers
        self.context = context
        super().__init__(self.detail)


class InfrastructureException(AppException):
    """Базовое исключение инфраструктуры."""
    status_code = 500
    detail = "Ошибка инфраструктуры"


class DatabaseException(InfrastructureException):
    """Базовое исключение базы данных."""
    detail = "Ошибка базы данных"


class DatabaseIntegrityError(DatabaseException):
    """Нарушение целостности БД (unique constraint, foreign key)."""
    status_code = 400
    detail = "Нарушение целостности данных"
    
    def __init__(self, constraint: Optional[str] = None, **context):
        if constraint:
            self.detail = f"Нарушение ограничения: {constraint}"
        super().__init__(**context)
        self.constraint = constraint


class DatabaseConnectionError(DatabaseException):
    """Ошибка подключения к БД."""
    status_code = 503
    detail = "Сервис временно недоступен"


class DatabaseNotFoundError(DatabaseException):
    """Запись не найдена в БД (низкоуровневая ошибка)."""
    status_code = 404
    detail = "Запись не найдена"


class DomainException(AppException):
    """Базовое исключение домена."""
    status_code = 400
    detail = "Ошибка бизнес-логики"


class NotFoundException(DomainException):
    """Ресурс не найден."""
    status_code = 404
    
    def __init__(
        self, 
        resource_type: str, 
        resource_id: Optional[int] = None,
        extra_info: Optional[str] = None,
        **context
    ):
        if resource_id:
            detail = f"{resource_type} с id={resource_id} не найден"
        else:
            detail = f"{resource_type} не найден"
        if extra_info:
            detail += f": {extra_info}"
        super().__init__(detail=detail, **context)
        self.resource_type = resource_type
        self.resource_id = resource_id


class ConflictException(DomainException):
    """Конфликт ресурсов (дубликат)."""
    status_code = 409
    
    def __init__(self, resource_type: str, field: str, value: Any, **context):
        detail = f"{resource_type} с {field}='{value}' уже существует"
        super().__init__(detail=detail, **context)
        self.resource_type = resource_type
        self.field = field
        self.value = value


class PermissionDeniedException(DomainException):
    """Доступ запрещён."""
    status_code = 403
    
    def __init__(self, action: str, resource_type: Optional[str] = None, **context):
        if resource_type:
            detail = f"{action} {resource_type} запрещено"
        else:
            detail = f"{action} запрещено"
        super().__init__(detail=detail, **context)
        self.action = action
        self.resource_type = resource_type


class ValidationError(DomainException):
    """Ошибка валидации бизнес-правил."""
    status_code = 400
    detail = "Ошибка валидации"
    
    def __init__(self, field: Optional[str] = None, message: Optional[str] = None, **context):
        if field and message:
            detail = f"Поле '{field}': {message}"
        elif message:
            detail = message
        else:
            detail = self.detail
        super().__init__(detail=detail, **context)
        self.field = field


class AuthenticationException(AppException):
    """Базовое исключение аутентификации."""
    status_code = 401
    detail = "Ошибка аутентификации"
    headers = {"WWW-Authenticate": "Bearer"}


class InvalidCredentialsException(AuthenticationException):
    """Неверные учётные данные."""
    detail = "Неверные учетные данные"


class InvalidTokenException(AuthenticationException):
    """Невалидный или истёкший токен."""
    detail = "Неверный или истёкший токен"


class UserNotFoundException(AuthenticationException):
    """Пользователь не найден."""
    detail = "Пользователь не найден"
