from sqlalchemy.orm import Session
from app.models.post import Post
from app.repositories.base import BaseRepository

class PostRepository(BaseRepository[Post]):
    def __init__(self, db: Session):
        super().__init__(Post, db)
    
    def get_by_author(self, author_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(Post).filter(
            Post.author_id == author_id
        ).offset(skip).limit(limit).all()
    
    def get_by_group(self, group_id: int, skip: int = 0, limit: int = 100):
        return self.db.query(Post).filter(
            Post.group_id == group_id
        ).offset(skip).limit(limit).all()
    
    def can_modify(self, post: Post, user_id: int) -> bool:
        """Проверка прав на редактирование/удаление"""
        return post.author_id == user_id
