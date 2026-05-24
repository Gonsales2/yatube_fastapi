from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.base import Base


class Post(Base):
    __tablename__ = "posts_post"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    pub_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    author_id = Column(Integer, ForeignKey("auth_user.id"), nullable=False, index=True)
    images = relationship(
        "PostImage", back_populates="post", cascade="all, delete-orphan"
    )
    group_id = Column(Integer, ForeignKey("posts_group.id"), nullable=True)

    author = relationship("User", back_populates="posts")
    group = relationship("Group", back_populates="posts")
    comments = relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Post(id={self.id}, text='{self.text[:30]}...')>"
