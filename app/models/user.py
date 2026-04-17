from datetime import datetime, timedelta
import uuid
from typing import Optional, Dict, Any

from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from app.database import Base
from app.config import settings
from app.schemas.base import UserCreate
from app.schemas.user import UserRead, Token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    calculations = relationship("Calculation", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(name={self.first_name} {self.last_name}, email={self.email})>"

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> Optional[uuid.UUID]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            return uuid.UUID(user_id) if user_id else None
        except (JWTError, ValueError):
            return None

    @classmethod
    def register(cls, db, user_data: Dict[str, Any]) -> "User":
        try:
            password = user_data.get("password", "")
            if len(password) < 6:
                raise ValueError("Password must be at least 6 characters long")

            existing_user = db.query(cls).filter(
                (cls.email == user_data.get("email")) |
                (cls.username == user_data.get("username"))
            ).first()

            if existing_user:
                raise ValueError("Username or email already exists")

            user_create = UserCreate.model_validate(user_data)

            new_user = cls(
                first_name=user_create.first_name,
                last_name=user_create.last_name,
                email=user_create.email,
                username=user_create.username,
                password=cls.hash_password(user_create.password),
                is_active=True,
                is_verified=False,
            )

            db.add(new_user)
            db.flush()
            return new_user

        except ValidationError as e:
            raise ValueError(str(e))
        except ValueError as e:
            raise e

    @classmethod
    def authenticate(cls, db, username: str, password: str) -> Optional[Dict[str, Any]]:
        user = db.query(cls).filter(
            (cls.username == username) | (cls.email == username)
        ).first()

        if not user or not user.verify_password(password):
            return None

        user.last_login = datetime.utcnow()
        db.commit()

        user_response = UserRead.model_validate(user)
        token_response = Token(
            access_token=cls.create_access_token({"sub": str(user.id)}),
            token_type="bearer",
            user=user_response,
        )

        return token_response.model_dump()