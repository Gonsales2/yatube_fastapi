from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_db, get_current_user
from app.repositories.post_repo import PostRepository
from app.repositories.group_repo import GroupRepository
from app.schemas.post import PostCreate, PostResponse, PostUpdate
from app.models.user import User
from app.models.post import Post

router = APIRouter()


@router.get("/", response_model=List[PostResponse])
def read_posts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список постов."""
    repo = PostRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{post_id}", response_model=PostResponse)
def read_post(
    post_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить пост по ID."""
    repo = PostRepository(db)
    post = repo.get(post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пост не найден"
        )
    
    return post


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post_in: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать новый пост."""
    if post_in.group is not None:
        group_repo = GroupRepository(db)
        if not group_repo.get(post_in.group):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Группа с указанным id не существует"
            )
    
    repo = PostRepository(db)
    create_data = post_in.model_dump()
    create_data["author_id"] = current_user.id
    
    return repo.create(create_data)


@router.patch("/{post_id}", response_model=PostResponse)
def update_post_partial(
    post_id: int = Path(..., ge=1),
    post_in: PostUpdate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Частично обновить пост (автор)."""
    repo = PostRepository(db)
    post = repo.get(post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пост не найден"
        )
    
    if not repo.can_modify(post, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Изменение чужого контента запрещено!"
        )

    if post_in.group is not None:
        group_repo = GroupRepository(db)
        if not group_repo.get(post_in.group):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Группа с указанным id не существует"
            )
    
    update_data = post_in.model_dump(exclude_unset=True)
    return repo.update(post, update_data)


@router.put("/{post_id}", response_model=PostResponse)
def update_post_full(
    post_id: int = Path(..., ge=1),
    post_in: PostUpdate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Полностью обновить пост (автор)."""
    repo = PostRepository(db)
    post = repo.get(post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пост не найден"
        )
    
    if not repo.can_modify(post, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Изменение чужого контента запрещено!"
        )

    if not post_in.text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Поле text обязательно для PUT-запроса"
        )

    if post_in.group is not None:
        group_repo = GroupRepository(db)
        if not group_repo.get(post_in.group):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Группа с указанным id не существует"
            )
    
    update_data = post_in.model_dump(exclude_unset=True)
    return repo.update(post, update_data)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить пост (только автор)."""
    repo = PostRepository(db)
    post = repo.get(post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пост не найден"
        )
    
    if not repo.can_modify(post, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Удаление чужого контента запрещено!"
        )
    
    repo.delete(post)
