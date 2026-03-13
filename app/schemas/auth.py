from pydantic import BaseModel, Field
from typing import Optional 


class Token(BaseModel):
    token: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserAuth(BaseModel):
    username: str = Field(..., min_length=1, max_length=150)
    password: str = Field(..., min_length=1)
