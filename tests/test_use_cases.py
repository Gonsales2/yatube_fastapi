import pytest

from app.schemas.post import PostCreate


@pytest.mark.asyncio
async def test_post_schema_validation():
    with pytest.raises(Exception):
        PostCreate(
            text="",
        )
