import hashlib
import uuid
from datetime import datetime

import jwt

import pytest

from src.configurations import Config
from src.enums import UserRole
from src.models import ActivationKey, User


config = Config()


@pytest.fixture
def db_with_not_active_user(db_empty):
    session = db_empty
    user = User()
    user.id = 1
    user.created_ts = datetime(2022, 9, 18)
    user.email = "str"
    user.first_name = "str"
    user.is_active = False
    user.password = hashlib.sha256("str".encode()).hexdigest()
    user.role = UserRole.admin
    user.second_name = "str"
    user.updated_ts = datetime(2022, 9, 18)
    session.add(user)
    session.commit()
    return session


@pytest.fixture
def db_with_activation_key(db_with_not_active_user):
    session = db_with_not_active_user
    session.add(
        ActivationKey(id=1, user_id=1, key=uuid.UUID("da7adade-dccd-4fa1-b37e-dd768310178e")),
    )
    session.commit()
    return session


@pytest.fixture
def db_with_admin_user(db_with_not_active_user):
    session = db_with_not_active_user
    user = session.query(User).get(1)
    user.is_active = True
    session.commit()
    return session


@pytest.fixture
def db_with_admin_and_regular_users(db_with_admin_user):
    session = db_with_admin_user
    user = User()
    user.id = 2
    user.created_ts = datetime(2022, 9, 18)
    user.email = "str2"
    user.first_name = "str2"
    user.is_active = True
    user.password = hashlib.sha256("str2".encode()).hexdigest()
    user.role = UserRole.regular
    user.second_name = "str2"
    user.updated_ts = datetime(2022, 9, 18)
    session.add(user)
    session.commit()
    return session


@pytest.fixture
def admin_token():
    return jwt.encode({"id": 1, "role": UserRole.admin.value, "exp": datetime.utcnow()}, Config().JWT_SECRET)


@pytest.fixture
def regular_token():
    return jwt.encode({"id": 2, "role": UserRole.regular.value, "exp": datetime.utcnow()}, Config().JWT_SECRET)
