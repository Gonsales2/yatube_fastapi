from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class CommentBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)

    @field_validator('text')
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Текст не может быть пустым')
        return v.strip()


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=1, max_length=10000)

    @field_validator('text')
    @classmethod
    def text_not_empty_if_provided(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError('Текст не может быть пустым')
        return v.strip() if v else v


class CommentResponse(BaseModel):
    id: int
    author: str
    text: str
    created: datetime
    post: int
    
    class Config:
        from_attributes = True
