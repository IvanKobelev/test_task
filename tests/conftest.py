from types import SimpleNamespace

from fastapi.testclient import TestClient

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from src.configurations import Config
from src.database import get_session
from src.views import app


config = Config()


@pytest.fixture
def fixtures(request):
    """Collection of fixtures declared via 'fixtures' mark."""
    fixtures = SimpleNamespace()
    if marker := request.node.get_closest_marker("fixtures"):
        for attr_name, fixture_config in marker.args[0].items():
            fixture = request.getfixturevalue(fixture_config)
            setattr(fixtures, attr_name, fixture)
    return fixtures


@pytest.fixture
def db_session():
    engine = create_engine(config.SQLALCHEMY_CONNECTION_URL)
    connection = engine.connect()
    transaction = connection.begin()
    session = scoped_session(sessionmaker(bind=connection))
    yield session
    transaction.rollback()
    session.remove()
    connection.close()


@pytest.fixture
def db_empty(db_session):
    return db_session


@pytest.fixture
def client(db_empty):
    def override_get_session():
        yield db_empty
    app.dependency_overrides[get_session] = override_get_session
    return TestClient(app)
