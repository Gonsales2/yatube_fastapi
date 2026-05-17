from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
import re


class PostBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    group: Optional[int] = Field(None, ge=1)

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Текст не может быть пустым")
        return " ".join(v.split())

    @field_validator("group")
    @classmethod
    def validate_group_id(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 1:
            raise ValueError("ID группы должен быть положительным числом")
        return v


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=1, max_length=10000)
    group: Optional[int] = Field(None, ge=1)

    @field_validator("text")
    @classmethod
    def text_not_empty_if_provided(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("Текст не может быть пустым")
            return " ".join(v.split())
        return v

    @field_validator("group")
    @classmethod
    def validate_group_id(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 1:
            raise ValueError("ID группы должен быть положительным числом")
        return v


class PostResponse(BaseModel):
    id: int
    author: str
    text: str
    pub_date: datetime
    image: Optional[str] = None
    group: Optional[int] = None

    class Config:
        from_attributes = True
