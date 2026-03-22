from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user
from app.repositories.group_repo import GroupRepository
from app.schemas.group import GroupResponse
from app.models.user import User
from app.use_cases.group_use_case import GroupUseCase
from app.repositories.group_repo import GroupRepository
from app.exceptions import AppException
from app.api.exception_handler import domain_to_http_exception
router = APIRouter()


@router.get("/", response_model=List[GroupResponse])
def read_groups(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        repo = GroupRepository(db)
        use_case = GroupUseCase(repo)
        return use_case.get_groups(skip=skip, limit=limit)
    except AppException as e:
        raise domain_to_http_exception(e)


@router.get("/{group_id}", response_model=GroupResponse)
def read_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        repo = GroupRepository(db)
        use_case = GroupUseCase(repo)
        return use_case.get_group(group_id=group_id)
    except AppException as e:
        raise domain_to_http_exception(e)
