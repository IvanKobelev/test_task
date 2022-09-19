"""Database connection."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from src.configurations import Config


config = Config()
engine = create_engine(config.SQLALCHEMY_CONNECTION_URL)
session = scoped_session(sessionmaker(bind=engine))


def get_session() -> Iterator[scoped_session]:
    """Fastapi dependency for database session."""
    try:
        yield session
    except Exception as err:
        session.rollback()
        raise err
    finally:
        session.remove()
