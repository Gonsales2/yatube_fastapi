from app.repositories.comment_repo import CommentRepository
from app.repositories.post_repo import PostRepository
from app.schemas.comment import CommentCreate, CommentUpdate
from app.exceptions import (
    NotFoundException,
    PermissionDeniedException,
    ValidationError,
)
from app.models.user import User


class CommentUseCase:
    def __init__(self, comment_repo: CommentRepository, post_repo: PostRepository):
        self.comment_repo = comment_repo
        self.post_repo = post_repo
    
    def get_comments(self, post_id: int, skip: int = 0, limit: int = 100) -> list:
        """Получить список комментариев поста."""
        if not self.post_repo.get(post_id):
            raise NotFoundException(resource_type="Пост", resource_id=post_id)
        
        comments = self.comment_repo.get_by_post(post_id, skip, limit)
        return [self._serialize(c) for c in comments]
    
    def get_comment(self, post_id: int, comment_id: int) -> dict:
        """Получить конкретный комментарий."""
        if not self.post_repo.get(post_id):
            raise NotFoundException(resource_type="Пост", resource_id=post_id)
        
        comment = self.comment_repo.get(comment_id)
        if not comment or comment.post_id != post_id:
            raise NotFoundException(resource_type="Комментарий", resource_id=comment_id)
        
        return self._serialize(comment)
    
    def create_comment(self, user: User, post_id: int, comment_in: CommentCreate) -> dict:
        """Создать комментарий."""
        if not self.post_repo.get(post_id):
            raise NotFoundException(resource_type="Пост", resource_id=post_id)

        if len(comment_in.text.strip()) < 2:
            raise ValidationError(
                field="text",
                message="Комментарий должен содержать минимум 2 символа"
            )
        
        create_data = comment_in.model_dump()
        create_data.update({"author_id": user.id, "post_id": post_id})
        
        comment = self.comment_repo.create(create_data)
        return self._serialize(comment)
    
    def update_comment(self, user: User, post_id: int, comment_id: int, 
                       comment_in: CommentUpdate, full_update: bool = False) -> dict:
        """Обновить комментарий."""
        comment = self.comment_repo.get(comment_id)
        if not comment or comment.post_id != post_id:
            raise NotFoundException(resource_type="Комментарий", resource_id=comment_id)
        
        if not self.comment_repo.can_modify(comment, user.id):
            raise PermissionDeniedException(action="Редактирование", resource_type="комментария")

        if full_update and comment_in.text and not comment_in.text.strip():
            raise ValidationError(field="text", message="Текст обязателен для полного обновления")
        
        update_data = comment_in.model_dump(exclude_unset=True)
        updated = self.comment_repo.update(comment, update_data)
        return self._serialize(updated)
    
    def delete_comment(self, user: User, post_id: int, comment_id: int) -> None:
        """Удалить комментарий."""
        comment = self.comment_repo.get(comment_id)
        if not comment or comment.post_id != post_id:
            raise NotFoundException(resource_type="Комментарий", resource_id=comment_id)
        
        if not self.comment_repo.can_modify(comment, user.id):
            raise PermissionDeniedException(action="Удаление", resource_type="комментария")
        
        self.comment_repo.delete(comment)
    
    @staticmethod
    def _serialize(comment) -> dict:
        return {
            "id": comment.id,
            "author": comment.author.username,
            "text": comment.text,
            "created": comment.created,
            "post": comment.post_id,
        }
