from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from app.database.base import Base
from app.exceptions import (
    DatabaseIntegrityError,
    DatabaseConnectionError,
    DatabaseException,
)

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepositoryAsync(Generic[ModelType]):

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: int) -> Optional[ModelType]:
        try:
            stmt = select(self.model).where(self.model.id == id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except OperationalError as e:
            raise DatabaseConnectionError() from e
        except SQLAlchemyError as e:
            raise DatabaseException() from e

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        try:
            stmt = select(self.model).offset(skip).limit(limit)
            result = await self.db.execute(stmt)
            return list(result.scalars().all())
        except OperationalError as e:
            raise DatabaseConnectionError() from e
        except SQLAlchemyError as e:
            raise DatabaseException() from e

    async def create(self, obj_in: dict) -> ModelType:
        try:
            db_obj = self.model(**obj_in)
            self.db.add(db_obj)
            await self.db.flush()
            await self.db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            await self.db.rollback()
            constraint = self._extract_constraint_name(e)
            raise DatabaseIntegrityError(constraint=constraint) from e
        except OperationalError as e:
            await self.db.rollback()
            raise DatabaseConnectionError() from e
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise DatabaseException() from e

    async def update(self, db_obj: ModelType, obj_in: dict) -> ModelType:
        try:
            for field, value in obj_in.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            await self.db.flush()
            await self.db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            await self.db.rollback()
            constraint = self._extract_constraint_name(e)
            raise DatabaseIntegrityError(constraint=constraint) from e
        except OperationalError as e:
            await self.db.rollback()
            raise DatabaseConnectionError() from e
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise DatabaseException() from e

    async def delete(self, db_obj: ModelType) -> None:
        try:
            await self.db.delete(db_obj)
            await self.db.flush()
        except IntegrityError as e:
            await self.db.rollback()
            constraint = self._extract_constraint_name(e)
            raise DatabaseIntegrityError(constraint=constraint) from e
        except OperationalError as e:
            await self.db.rollback()
            raise DatabaseConnectionError() from e
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise DatabaseException() from e

    @staticmethod
    def _extract_constraint_name(error: IntegrityError) -> Optional[str]:
        if hasattr(error, "orig") and hasattr(error.orig, "args"):
            msg = str(error.orig)
            if "unique constraint" in msg.lower():
                parts = msg.split('"')
                if len(parts) >= 2:
                    return parts[1]
        return None
