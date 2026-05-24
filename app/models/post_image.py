from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.base import Base


class PostImage(Base):
    __tablename__ = "posts_postimage"

    id = Column(Integer, primary_key=True, index=True)
    image = Column(String(500), nullable=False)
    order = Column(Integer, default=0, index=True)
    post_id = Column(Integer, ForeignKey("posts_post.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    post = relationship("Post", back_populates="images")
