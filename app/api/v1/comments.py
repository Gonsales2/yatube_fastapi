"""Comment endpoints for YaTube API."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.comment_repo import CommentRepository
from app.repositories.post_repo import PostRepository
from app.schemas.comment import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
)


router = APIRouter()


@router.get("/", response_model=List[CommentResponse])
def read_comments(
    post_id: int = Path(..., ge=1),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get list of comments for a post."""
    post_repo = PostRepository(db)
    if not post_repo.get(post_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пост не найден",
        )

    repo = CommentRepository(db)
    return repo.get_by_post(post_id=post_id, skip=skip, limit=limit)


@router.get("/{comment_id}", response_model=CommentResponse)
def read_comment(
    post_id: int = Path(..., ge=1),
    comment_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get comment by ID."""
    post_repo = PostRepository(db)
    if not post_repo.get(post_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пост не найден",
        )

    repo = CommentRepository(db)
    comment = repo.get(comment_id)

    if not comment or comment.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комментарий не найден",
        )

    return comment


@router.post(
    "/",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    post_id: int = Path(..., ge=1),
    comment_in: CommentCreate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new comment for a post."""
    post_repo = PostRepository(db)
    post = post_repo.get(post_id)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пост не найден",
        )

    repo = CommentRepository(db)

    create_data = comment_in.model_dump()
    create_data["author_id"] = current_user.id
    create_data["post_id"] = post_id

    return repo.create(create_data)


@router.patch("/{comment_id}", response_model=CommentResponse)
def update_comment_partial(
    post_id: int = Path(..., ge=1),
    comment_id: int = Path(..., ge=1),
    comment_in: CommentUpdate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Partially update a comment (author only)."""
    repo = CommentRepository(db)
    comment = repo.get(comment_id)

    if not comment or comment.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комментарий не найден",
        )

    if not repo.can_modify(comment, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Изменение чужого комментария запрещено!",
        )

    update_data = comment_in.model_dump(exclude_unset=True)
    return repo.update(comment, update_data)


@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment_full(
    post_id: int = Path(..., ge=1),
    comment_id: int = Path(..., ge=1),
    comment_in: CommentUpdate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fully update a comment (author only)."""
    repo = CommentRepository(db)
    comment = repo.get(comment_id)

    if not comment or comment.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комментарий не найден",
        )

    if not repo.can_modify(comment, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Изменение чужого комментария запрещено!",
        )

    if not comment_in.text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Поле text обязательно для PUT-запроса",
        )

    update_data = comment_in.model_dump(exclude_unset=True)
    return repo.update(comment, update_data)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    post_id: int = Path(..., ge=1),
    comment_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a comment (author only)."""
    repo = CommentRepository(db)
    comment = repo.get(comment_id)

    if not comment or comment.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комментарий не найден",
        )

    if not repo.can_modify(comment, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Удаление чужого комментария запрещено!",
        )

    repo.delete(comment)
