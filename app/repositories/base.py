from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError, DataError
from app.database.base import Base
from app.exceptions import (
    DatabaseIntegrityError, 
    DatabaseConnectionError, 
    DatabaseException,
    DatabaseNotFoundError
)

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    def get(self, id: int) -> Optional[ModelType]:
        """Получить запись по ID с обработкой ошибок БД."""
        try:
            return self.db.query(self.model).filter(self.model.id == id).first()
        except OperationalError as e:
            raise DatabaseConnectionError() from e
        except (DataError, IntegrityError) as e:
            raise DatabaseIntegrityError(constraint=str(e.orig) if hasattr(e, 'orig') else None) from e
        except SQLAlchemyError as e:
            raise DatabaseException() from e
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Получить список записей с обработкой ошибок БД."""
        try:
            return self.db.query(self.model).offset(skip).limit(limit).all()
        except OperationalError as e:
            raise DatabaseConnectionError() from e
        except SQLAlchemyError as e:
            raise DatabaseException() from e
    
    def create(self, obj_create: dict) -> ModelType:
        """Создать запись с обработкой ошибок БД."""
        try:
            obj = self.model(**obj_create)
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except IntegrityError as e:
            self.db.rollback()
            constraint = self._extract_constraint_name(e)
            raise DatabaseIntegrityError(constraint=constraint) from e
        except OperationalError as e:
            self.db.rollback()
            raise DatabaseConnectionError() from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseException() from e
    
    def update(self, db_obj: ModelType, obj_update: dict) -> ModelType:
        """Обновить запись с обработкой ошибок БД."""
        try:
            for field, value in obj_update.items():
                setattr(db_obj, field, value)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            self.db.rollback()
            constraint = self._extract_constraint_name(e)
            raise DatabaseIntegrityError(constraint=constraint) from e
        except OperationalError as e:
            self.db.rollback()
            raise DatabaseConnectionError() from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseException() from e
    
    def delete(self, db_obj: ModelType) -> None:
        """Удалить запись с обработкой ошибок БД."""
        try:
            self.db.delete(db_obj)
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            constraint = self._extract_constraint_name(e)
            raise DatabaseIntegrityError(constraint=constraint) from e
        except OperationalError as e:
            self.db.rollback()
            raise DatabaseConnectionError() from e
        except SQLAlchemyError as e:
            self.db.rollback()
            raise DatabaseException() from e
    
    @staticmethod
    def _extract_constraint_name(error: IntegrityError) -> Optional[str]:
        """Извлечь имя нарушенного ограничения из ошибки SQLAlchemy."""
        if hasattr(error, 'orig') and hasattr(error.orig, 'args'):
            # Для PostgreSQL: constraint name обычно в сообщении
            msg = str(error.orig)
            if 'unique constraint' in msg.lower():
                parts = msg.split('"')
                if len(parts) >= 2:
                    return parts[1]
        return None
