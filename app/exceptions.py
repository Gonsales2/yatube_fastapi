from typing import Optional, Dict, Any


class AppException(Exception):
    status_code: int = 500
    detail: str = "Внутренняя ошибка сервера"
    headers: Optional[Dict[str, str]] = None

    def __init__(
        self,
        detail: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **context: Any,
    ):
        if detail:
            self.detail = detail
        if headers:
            self.headers = headers
        self.context = context
        super().__init__(self.detail)


class InfrastructureException(AppException):
    status_code = 500
    detail = "Ошибка инфраструктуры"


class DatabaseException(InfrastructureException):
    detail = "Ошибка базы данных"


class DatabaseIntegrityError(DatabaseException):
    status_code = 400
    detail = "Нарушение целостности данных"

    def __init__(self, constraint: Optional[str] = None, **context):
        if constraint:
            self.detail = f"Нарушение ограничения: {constraint}"
        super().__init__(**context)
        self.constraint = constraint


class DatabaseConnectionError(DatabaseException):
    status_code = 503
    detail = "Сервис временно недоступен"


class DatabaseNotFoundError(DatabaseException):
    status_code = 404
    detail = "Запись не найдена"


class DomainException(AppException):
    status_code = 400
    detail = "Ошибка бизнес-логики"


class NotFoundException(DomainException):
    status_code = 404

    def __init__(
        self,
        resource_type: str,
        resource_id: Optional[int] = None,
        extra_info: Optional[str] = None,
        **context,
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
    status_code = 409

    def __init__(self, resource_type: str, field: str, value: Any, **context):
        detail = f"{resource_type} с {field}='{value}' уже существует"
        super().__init__(detail=detail, **context)
        self.resource_type = resource_type
        self.field = field
        self.value = value


class PermissionDeniedException(DomainException):
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
    status_code = 400
    detail = "Ошибка валидации"

    def __init__(
        self, field: Optional[str] = None, message: Optional[str] = None, **context
    ):
        if field and message:
            detail = f"Поле '{field}': {message}"
        elif message:
            detail = message
        else:
            detail = self.detail
        super().__init__(detail=detail, **context)
        self.field = field


class AuthenticationException(AppException):
    status_code = 401
    detail = "Ошибка аутентификации"
    headers = {"WWW-Authenticate": "Bearer"}


class InvalidCredentialsException(AuthenticationException):
    detail = "Неверные учетные данные"


class InvalidTokenException(AuthenticationException):
    detail = "Неверный или истёкший токен"


class UserNotFoundException(AuthenticationException):
    detail = "Пользователь не найден"
