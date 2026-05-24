from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.base import Base


class CommentImage(Base):
    __tablename__ = "posts_commentimage"

    id = Column(Integer, primary_key=True, index=True)
    image = Column(String(500), nullable=False)
    order = Column(Integer, default=0, index=True)
    comment_id = Column(Integer, ForeignKey("posts_comment.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    comment = relationship("Comment", back_populates="images")

    def __repr__(self):
        return f"<CommentImage(id={self.id}, comment_id={self.comment_id}, order={self.order})>"
