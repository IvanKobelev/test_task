"""Endpoints."""

import uuid

from fastapi import Depends

from sqlalchemy.orm import Session

from src import app, services
from src.database import get_session
from src.rabbitmq import RabbitMQ
from src.schemas import BasicOut, CreateUserIn, ErrorOut, LoginUserIn, LoginUserOut, TokenData, UpdateUserIn, UserOut
from src.security import decode_token


@app.get("/ping")
def health_check() -> str:
    """Health check endpoint."""
    return "pong"


@app.post("/users/sign-up", responses={200: {"model": BasicOut}, 400: {"model": ErrorOut}})
def create_new_user(
    user_data: CreateUserIn, session: Session = Depends(get_session), rabbitmq: RabbitMQ = Depends(RabbitMQ),
) -> BasicOut:
    """Create new user."""
    return services.create_new_user(user_data, session, rabbitmq)


@app.post("/users/sign-in", responses={
    200: {"model": LoginUserOut}, 400: {"model": ErrorOut}, 404: {"model": ErrorOut},
})
def login_user(user_data: LoginUserIn, session: Session = Depends(get_session)) -> LoginUserOut:
    """Login user."""
    return services.login_user(user_data, session)


@app.get("/users/activate/{key}", responses={200: {"model": BasicOut}, 404: {"model": ErrorOut}})
def activate_user(key: uuid.UUID, session: Session = Depends(get_session)) -> BasicOut:
    """Activate user."""
    return services.activate_user(key, session)


@app.get("/users/{user_id}", responses={
    200: {"model": UserOut}, 403: {"model": ErrorOut}, 404: {"model": ErrorOut},
})
def get_user(
    user_id: int, token_data: TokenData = Depends(decode_token), session: Session = Depends(get_session),
) -> UserOut:
    """Get user's data."""
    return services.get_user(user_id, token_data, session)


@app.patch("/users/{user_id}", responses={
    200: {"model": UserOut}, 403: {"model": ErrorOut}, 404: {"model": ErrorOut},
})
def update_user(
    user_id: int,
    user_data: UpdateUserIn,
    token_data: TokenData = Depends(decode_token),
    session: Session = Depends(get_session),
) -> UserOut:
    """Update user's data."""
    return services.update_user(user_id, user_data, token_data, session)
