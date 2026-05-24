from datetime import datetime, timedelta
from jose import jwt
from app.config import settings


class JWTService:
    def __init__(self, config=settings):
        self.secret = config.SECRET_KEY
        self.algorithm = config.ALGORITHM
        self.access_expire = config.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_expire = getattr(config, "REFRESH_TOKEN_EXPIRE_DAYS", 30)

    def create_access_token(self, username: str) -> str:
        expire = datetime.utcnow() + timedelta(minutes=self.access_expire)
        return jwt.encode(
            {"sub": username, "exp": expire, "type": "access"},
            self.secret,
            algorithm=self.algorithm,
        )

    def create_refresh_token(self) -> str:
        expire = datetime.utcnow() + timedelta(days=self.refresh_expire)
        return jwt.encode(
            {"exp": expire, "type": "refresh"},
            self.secret,
            algorithm=self.algorithm,
        )
