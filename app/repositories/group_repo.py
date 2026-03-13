from sqlalchemy.orm import Session
from app.models.group import Group
from app.repositories.base import BaseRepository

class GroupRepository(BaseRepository[Group]):
    def __init__(self, db: Session):
        super().__init__(Group, db)
    
    def get_by_slug(self, slug: str) -> Group | None:
        return self.db.query(Group).filter(Group.slug == slug).first()
