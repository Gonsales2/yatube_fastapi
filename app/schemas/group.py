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


class GroupInDB(GroupBase):
    id: int

    class Config:
        from_attributes = True


class GroupResponse(GroupInDB):
    pass
