from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user
from app.repositories.group_repo import GroupRepository
from app.schemas.group import GroupResponse
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[GroupResponse])
def read_groups(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список групп (только для авторизованных пользователей)."""
    repo = GroupRepository(db)
    return repo.get_all(skip=skip, limit=limit)


@router.get("/{group_id}", response_model=GroupResponse)
def read_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить информацию о группе по ID."""
    repo = GroupRepository(db)
    group = repo.get(group_id)
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Группа не найдена"
        )
    
    return group
