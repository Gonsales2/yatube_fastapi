from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.base import BaseRepository
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()
    
    def create_user(self, username: str, email: str, password: str) -> User:
        hashed_password = pwd_context.hash(password)
        return self.create({
            "username": username,
            "email": email,
            "password": hashed_password
        })
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
