"""Services for endpoints."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from fastapi import HTTPException

from src.cash_controller import delete_user_from_cache, get_user_from_cache
from src.configurations import Config
from src.enums import UserRole
from src.models import ActivationKey, User
from src.schemas import (
    BasicOut, CreateUserIn, LoginUserIn, LoginUserOut, QueueMessage, TokenData, UpdateUserIn, UserOut,
)
from src.security import encode_token

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from src.rabbitmq import RabbitMQ


config = Config()


def create_new_user(user_data: CreateUserIn, session: Session, rabbitmq: RabbitMQ) -> BasicOut:
    """Create new user service."""
    existed_user = User.get_by_email(session, user_data.email)
    if existed_user is not None:
        raise HTTPException(status_code=400, detail=f"User with email {user_data.email} is already exists.")
    user = User.create(session, user_data)
    uuid_key = uuid.uuid4()
    ActivationKey.match_user_key(session, user.id, uuid_key)
    message = QueueMessage(email=user.email, message=f"{config.SERVICE_HOST}/users/activate/{uuid_key}")
    rabbitmq.publish_message_to_queue(message)
    return BasicOut(message=f"Activate your profile by link in email. (For testing: {uuid_key})")


def login_user(user_data: LoginUserIn, session: Session) -> LoginUserOut:
    """Login user service."""
    user = User.get_active_by_email(session, user_data.email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.compare_passwords(session, user_data.password) is False:
        raise HTTPException(status_code=400, detail="Incorrect password.")
    token_data = TokenData.from_orm(user)
    return LoginUserOut(user=UserOut.from_orm(user), token=encode_token(token_data))


def activate_user(key: uuid.UUID, session: Session) -> BasicOut:
    """Activate user service."""
    user = User.get_by_key(session, key)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    user.activate(session)
    return BasicOut(message="User's profile is active.")


def get_user(user_id: int, token_data: TokenData, session: Session) -> UserOut:
    """Get user's data service."""
    if user_id != token_data.id and token_data.role != UserRole.admin.value:
        raise HTTPException(status_code=403, detail="No permissions.")
    return get_user_from_cache(user_id, session)


def update_user(user_id: int, user_data: UpdateUserIn, token_data: TokenData, session: Session) -> UserOut:
    """Update user's data service."""
    if user_id != token_data.id and token_data.role != UserRole.admin.value:
        raise HTTPException(status_code=403, detail="No permissions.")
    user = User.get_active_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    updated_user = user.update(session, user_data)
    delete_user_from_cache(user_id)
    return UserOut.from_orm(updated_user)
