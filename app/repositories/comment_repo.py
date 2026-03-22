from sqlalchemy.orm import Session
from app.models.comment import Comment
from app.repositories.base import BaseRepository
from sqlalchemy.exc import IntegrityError, OperationalError
from app.exceptions import DatabaseIntegrityError, DatabaseConnectionError

class CommentRepository(BaseRepository[Comment]):
    def __init__(self, db: Session):
        super().__init__(Comment, db)
    
    def can_modify(self, comment: Comment, user_id: int) -> bool:
        return comment.author_id == user_id
    def get_by_post(self, post_id: int, skip: int = 0, limit: int = 100):
        """Получить комментарии поста с обработкой ошибок."""
        try:
            return self.db.query(Comment).filter(
                Comment.post_id == post_id
            ).order_by(Comment.created).offset(skip).limit(limit).all()
        except OperationalError as e:
            raise DatabaseConnectionError() from e
        except Exception as e:
            raise DatabaseIntegrityError(constraint=str(e.orig) if hasattr(e, 'orig') else None) from e

    def create(self, obj_create: dict):
        """Переопределяем create для обработки уникальности."""
        try:
            return super().create(obj_create)
        except DatabaseIntegrityError as e:
            if e.constraint and 'unique' in e.constraint.lower():
                pass
            raise
