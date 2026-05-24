import re

from pydantic import BaseModel, Field, field_validator


class GroupBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=50, pattern=r"^[-a-zA-Z0-9_]+$")
    description: str = Field(..., min_length=1)

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r"^[-a-z0-9_]+$", v):
            raise ValueError("Slug может содержать только строчные буквы, цифры, - и _")
        if len(v) > 50:
            raise ValueError("Slug не может быть длиннее 50 символов")
        return v


class GroupCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1, max_length=500)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Название группы не может быть пустым")
        if len(v) > 200:
            raise ValueError("Название не может быть длиннее 200 символов")
        return v

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r"^[-a-z0-9_]+$", v):
            raise ValueError(
                "Slug может содержать только строчные латинские буквы, цифры, дефис и подчёркивание"
            )
        if len(v) > 50:
            raise ValueError("Slug не может быть длиннее 50 символов")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Описание не может быть пустым")
        if len(v) > 500:
            raise ValueError("Описание не может быть длиннее 500 символов")
        return v


class GroupInDB(GroupBase):
    id: int

    class Config:
        from_attributes = True


class GroupResponse(GroupInDB):
    pass
