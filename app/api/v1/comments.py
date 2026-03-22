from typing import List
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.comment_repo import CommentRepository
from app.repositories.post_repo import PostRepository
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.use_cases.comment_use_case import CommentUseCase
from app.exceptions import AppException
from app.api.exception_handler import domain_to_http_exception

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
    try:
        comment_repo = CommentRepository(db)
        post_repo = PostRepository(db)
        use_case = CommentUseCase(comment_repo, post_repo)
        return use_case.get_comments(post_id=post_id, skip=skip, limit=limit)
    except AppException as e:
        raise domain_to_http_exception(e)


@router.get("/{comment_id}", response_model=CommentResponse)
def read_comment(
    post_id: int = Path(..., ge=1),
    comment_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get comment by ID."""
    try:
        comment_repo = CommentRepository(db)
        post_repo = PostRepository(db)
        use_case = CommentUseCase(comment_repo, post_repo)
        return use_case.get_comment(post_id=post_id, comment_id=comment_id)
    except AppException as e:
        raise domain_to_http_exception(e)


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: int = Path(..., ge=1),
    comment_in: CommentCreate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new comment for a post."""
    try:
        comment_repo = CommentRepository(db)
        post_repo = PostRepository(db)
        use_case = CommentUseCase(comment_repo, post_repo)
        return use_case.create_comment(
            user=current_user,
            post_id=post_id,
            comment_in=comment_in
        )
    except AppException as e:
        raise domain_to_http_exception(e)


@router.patch("/{comment_id}", response_model=CommentResponse)
def update_comment_partial(
    post_id: int = Path(..., ge=1),
    comment_id: int = Path(..., ge=1),
    comment_in: CommentUpdate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Partially update a comment (author only)."""
    try:
        comment_repo = CommentRepository(db)
        post_repo = PostRepository(db)
        use_case = CommentUseCase(comment_repo, post_repo)
        return use_case.update_comment(
            user=current_user,
            post_id=post_id,
            comment_id=comment_id,
            comment_in=comment_in,
            full_update=False
        )
    except AppException as e:
        raise domain_to_http_exception(e)


@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment_full(
    post_id: int = Path(..., ge=1),
    comment_id: int = Path(..., ge=1),
    comment_in: CommentUpdate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fully update a comment (author only)."""
    try:
        comment_repo = CommentRepository(db)
        post_repo = PostRepository(db)
        use_case = CommentUseCase(comment_repo, post_repo)
        return use_case.update_comment(
            user=current_user,
            post_id=post_id,
            comment_id=comment_id,
            comment_in=comment_in,
            full_update=True
        )
    except AppException as e:
        raise domain_to_http_exception(e)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    post_id: int = Path(..., ge=1),
    comment_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a comment (author only)."""
    try:
        comment_repo = CommentRepository(db)
        post_repo = PostRepository(db)
        use_case = CommentUseCase(comment_repo, post_repo)
        use_case.delete_comment(
            user=current_user,
            post_id=post_id,
            comment_id=comment_id
        )
        return None
    except AppException as e:
        raise domain_to_http_exception(e)
