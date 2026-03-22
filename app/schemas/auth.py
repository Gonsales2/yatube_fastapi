from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional
import re


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    @property
    def token(self) -> str:
        return self.access_token

class TokenData(BaseModel):
    username: Optional[str] = None


class UserAuth(BaseModel):
    username: str = Field(..., min_length=1, max_length=150)
    password: str = Field(..., min_length=1)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Имя пользователя не может быть пустым')
        if len(v) > 150:
            raise ValueError('Имя пользователя не может быть длиннее 150 символов')
        if not re.match(r'^[\w.@+-]+$', v):
            raise ValueError(
                'Имя пользователя может содержать только буквы, цифры, '
                'и символы: @ . + - _'
            )
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Пароль не может быть длиннее 72 байт')
        return v


class UserRegister(BaseModel):
    username: str = Field(..., min_length=1, max_length=150)
    password: str = Field(..., min_length=8)
    email: Optional[str] = None
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Имя пользователя не может быть пустым')
        if not re.match(r'^[\w.@+-]+$', v):
            raise ValueError('Имя пользователя содержит недопустимые символы')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        password_bytes = v.encode('utf-8')
        if len(password_bytes) > 72:
            raise ValueError('Пароль не может быть длиннее 72 байт')
        if len(v) < 8:
            raise ValueError('Пароль должен содержать минимум 8 символов')
        has_letter = bool(re.search(r'[A-Za-zа-яА-ЯёЁ]', v))
        has_digit = bool(re.search(r'\d', v))
        if not (has_letter and has_digit):
            raise ValueError('Пароль должен содержать хотя бы одну букву и одну цифру')
        return v
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip().lower()
        if not v:
            return None
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError('Неверный формат email')
        if len(v) > 254:
            raise ValueError('Email не может быть длиннее 254 символов')
        return v
