from pydantic import BaseModel, Field, field_validator
from typing import Optional

class Token(BaseModel):
    token: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserAuth(BaseModel):
    username: str = Field(..., min_length=1, max_length=150)
    password: str = Field(..., min_length=1)
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
    
    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Пароль не может быть длиннее 72 байт')
        return v
