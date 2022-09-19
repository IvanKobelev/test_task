"""Cache controller."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import HTTPException

from src.models import User
from src.schemas import UserOut

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def get_user_from_cache(user_id: int, session: Session) -> UserOut:
    """Get user's data from cache or create new cache."""
    path_to_file = Path("cache") / f"{user_id}.json"
    if path_to_file.exists() is False:
        return create_user_cache(user_id, session)
    return UserOut.parse_file(path_to_file)


def create_user_cache(user_id: int, session: Session) -> UserOut:
    """Create new user's cache."""
    user = User.get_active_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    user_data = UserOut.from_orm(user)
    path_to_file = Path("cache") / f"{user_id}.json"
    with open(path_to_file, "w") as f:
        json.dump(user_data.dict(), f)
    return user_data


def delete_user_from_cache(user_id: int) -> None:
    """Delete user's data from cache."""
    path_to_file = Path("cache") / f"{user_id}.json"
    if path_to_file.exists():
        path_to_file.unlink()
