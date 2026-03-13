from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class PostBase(BaseModel):
    """Базовая схема для поста"""
    text: str = Field(..., min_length=1, max_length=10000)
    group: Optional[int] = None

    @field_validator('text')
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Текст не может быть пустым')
        return v.strip()


class PostCreate(PostBase):
    """Схема для создания поста (запрос)"""
    pass


class PostUpdate(BaseModel):
    """Схема для обновления поста (PATCH/PUT) — все поля опциональны"""
    text: Optional[str] = Field(None, min_length=1, max_length=10000)
    group: Optional[int] = None

    @field_validator('text')
    @classmethod
    def text_not_empty_if_provided(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Текст не может быть пустым')
        return v.strip() if v else v


class PostInDB(PostBase):
    """Внутренняя схема поста из БД"""
    id: int
    author_id: int
    pub_date: datetime
    image: Optional[str] = None
    
    class Config:
        from_attributes = True


class PostResponse(BaseModel):
    """Публичная схема ответа — то, что видит клиент"""
    id: int
    author: str
    text: str
    pub_date: datetime
    image: Optional[str] = None
    group: Optional[int] = None
    
    class Config:
        from_attributes = True
