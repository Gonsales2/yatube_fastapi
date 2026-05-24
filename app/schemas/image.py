from pydantic import BaseModel


class ImageResponse(BaseModel):
    id: int
    image: str
    order: int
    url: str

    class Config:
        from_attributes = True


class ImageInCreate(BaseModel):
    image: str
    order: int = 0
