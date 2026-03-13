from sqlalchemy.orm import Session
from app.models.comment import Comment
from app.repositories.base import BaseRepository

class CommentRepository(BaseRepository[Comment]):
    def __init__(self, db: Session):
        super().__init__(Comment, db)
    
    def get_by_post(self, post_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(Comment).filter(
            Comment.post_id == post_id
        ).order_by(Comment.created).offset(skip).limit(limit).all()
    
    def can_modify(self, comment: Comment, user_id: int) -> bool:
        return comment.author_id == user_id
