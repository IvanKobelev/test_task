"""Database models."""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session, declarative_base

from src.enums import UserRole

if TYPE_CHECKING:
    from src.schemas import CreateUserIn, UpdateUserIn


Base = declarative_base()


class User(Base):
    """User model."""

    __tablename__ = "user"

    id: int = Column(Integer, primary_key=True)
    created_ts = Column(DateTime, default=datetime.utcnow)
    email = Column(String(512), nullable=False, unique=True)
    first_name = Column(String(512), nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
    password = Column(Text, nullable=False)
    role = Column(Enum(UserRole, values_callable=lambda enum: [e.value for e in enum]), default=UserRole.regular)
    second_name = Column(String(512), nullable=False)
    updated_ts = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def create(cls, session: Session, user_data: CreateUserIn) -> User:
        """Create new user."""
        user = User()
        user.email = user_data.email
        user.first_name = user_data.first_name
        user.password = hashlib.sha256(user_data.password.encode()).hexdigest()
        user.second_name = user_data.second_name
        session.add(user)
        session.commit()
        return user

    @classmethod
    def get_active_by_id(cls, session: Session, user_id: int) -> User | None:
        """Get active user by id if exists."""
        return session.query(User).filter(User.id == user_id).filter(User.is_active.is_(True)).first()

    @classmethod
    def get_active_by_email(cls, session: Session, email: str) -> User | None:
        """Get active user by email if exists."""
        return session.query(User).filter(User.email == email).filter(User.is_active.is_(True)).first()

    @classmethod
    def get_by_email(cls, session: Session, email: str) -> User | None:
        """Get user by email if exists."""
        return session.query(User).filter(User.email == email).first()

    @classmethod
    def get_by_key(cls, session: Session, key: uuid.UUID) -> User | None:
        """Get user by activation key if exists."""
        return session.query(User) \
                      .select_from(ActivationKey) \
                      .filter(ActivationKey.key == key) \
                      .join(User, User.id == ActivationKey.user_id).first()

    def update(self, session: Session, user_data: UpdateUserIn) -> User:
        """Update user."""
        for attr, value in user_data.dict(exclude_none=True).items():
            setattr(self, attr, value)
        session.commit()
        return self

    def activate(self, session: Session) -> None:
        """Activate user."""
        self.is_active = True
        session.commit()

    def compare_passwords(self, session: Session, password: str) -> bool:
        """Compare passwords."""
        return self.password == hashlib.sha256(password.encode()).hexdigest()


class ActivationKey(Base):
    """ActivationKey model."""

    __tablename__ = "activation_key"

    id: int = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    key = Column(UUID(as_uuid=True), nullable=False, unique=True)

    @classmethod
    def match_user_key(cls, session: Session, user_id: int, key: uuid.UUID) -> None:
        """Match user with generated uuid key."""
        activation_key = session.query(ActivationKey).filter(ActivationKey.user_id == user_id).first()
        if activation_key is None:
            activation_key = ActivationKey(user_id=user_id)
        activation_key.key = key
        session.add(activation_key)
        session.commit()
