from sqlalchemy.orm import Session
from app.models.post import Post
from app.repositories.base import BaseRepository
from sqlalchemy.exc import IntegrityError, OperationalError
from app.exceptions import DatabaseIntegrityError, DatabaseConnectionError, ConflictException

class PostRepository(BaseRepository[Post]):
    def __init__(self, db: Session):
        super().__init__(Post, db)

    def create(self, obj_create: dict):
        """Создание поста с обработкой ошибок БД."""
        try:
            return super().create(obj_create)
        except DatabaseIntegrityError as e:
            if e.constraint and 'group_id' in e.constraint.lower():
                raise ConflictException(
                    resource_type="Пост",
                    field="group",
                    value=obj_create.get("group_id")
                ) from e
            raise

    def get_by_author(self, author_id: int, skip: int = 0, limit: int = 100):
        """Добавить try/except как в base.py"""
        try:
            return self.db.query(Post).filter(
                Post.author_id == author_id
            ).offset(skip).limit(limit).all()
        except OperationalError as e:
            raise DatabaseConnectionError() from e
        except Exception as e:
            raise DatabaseIntegrityError() from e
    
    def get_by_group(self, group_id: int, skip: int = 0, limit: int = 100):
        try:
            return self.db.query(Post).filter(
                Post.group_id == group_id
            ).offset(skip).limit(limit).all()
        except OperationalError as e:
            raise DatabaseConnectionError() from e
        except Exception as e:
            raise DatabaseIntegrityError() from e
    
    def can_modify(self, post: Post, user_id: int) -> bool:
        """Проверка прав на редактирование/удаление"""
        return post.author_id == user_id
