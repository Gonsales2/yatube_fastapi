from pydantic import BaseModel, Field


class GroupBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=50, pattern=r'^[-a-zA-Z0-9_]+$')
    description: str = Field(..., min_length=1)


class GroupInDB(GroupBase):
    id: int
    
    class Config:
        from_attributes = True


class GroupResponse(GroupInDB):
    """Группы — только чтение"""
    pass
