from app.repositories.group_repo import GroupRepository
from app.exceptions import NotFoundException
from typing import List


class GroupUseCase:
    def __init__(self, group_repo: GroupRepository):
        self.group_repo = group_repo
    
    def get_groups(self, skip: int = 0, limit: int = 100) -> List[dict]:
        """Получить список групп."""
        groups = self.group_repo.get_all(skip, limit)
        return [self._serialize(g) for g in groups]
    
    def get_group(self, group_id: int) -> dict:
        """Получить группу по ID."""
        group = self.group_repo.get(group_id)
        if not group:
            raise NotFoundException(resource_type="Группа", resource_id=group_id)
        return self._serialize(group)
    
    def get_group_by_slug(self, slug: str) -> dict:
        """Получить группу по slug."""
        group = self.group_repo.get_by_slug(slug)
        if not group:
            raise NotFoundException(resource_type="Группа", extra_info=f"slug='{slug}'")
        return self._serialize(group)
    
    @staticmethod
    def _serialize(group) -> dict:
        return {
            "id": group.id,
            "title": group.title,
            "slug": group.slug,
            "description": group.description,
        }
