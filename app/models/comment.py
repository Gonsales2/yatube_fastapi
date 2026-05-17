from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.base import Base


class Comment(Base):
    __tablename__ = "posts_comment"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    created = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    author_id = Column(Integer, ForeignKey("auth_user.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts_post.id"), nullable=False)

    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

    def __repr__(self):
        return f"<Comment(id={self.id}, post_id={self.post_id})>"
