import hashlib
import uuid
from datetime import datetime
from pathlib import Path

import jwt

import pytest

from src.configurations import Config
from src.enums import UserRole
from src.models import ActivationKey, User
from src.schemas import UserOut


config = Config()


@pytest.mark.fixtures({"client": "client"})
def test_health_check_returns_correct_response(fixtures):
    result = fixtures.client.get("/ping")

    assert result.status_code == 200
    assert result.json() == "pong"


@pytest.mark.fixtures({"client": "client", "db": "db_empty"})
def test_create_new_user_returns_422(fixtures):
    json = {
        "email": "str",
        "first_name": "str",
        "password": "str",
    }

    result = fixtures.client.post("/users/sign-up", json=json)

    assert result.status_code == 422
    assert result.json()["detail"] == [
        {"loc": ["body", "second_name"], "msg": "field required", "type": "value_error.missing"},
    ]


@pytest.mark.fixtures({"client": "client", "db": "db_with_not_active_user"})
def test_create_new_user_with_not_unique_email_returns_400(fixtures):
    json = {
        "email": "str",
        "first_name": "str",
        "password": "str",
        "second_name": "str",
    }

    result = fixtures.client.post("/users/sign-up", json=json)

    assert result.status_code == 400
    assert result.json()["detail"] == f"User with email {json['email']} is already exists."


@pytest.mark.fixtures({"client": "client", "db": "db_empty"})
def test_create_new_user_returns_correct_response(fixtures):
    json = {
        "email": "str",
        "first_name": "str",
        "password": "str",
        "second_name": "str",
    }

    result = fixtures.client.post("/users/sign-up", json=json)

    assert result.status_code == 200
    assert result.json()["message"].startswith("Activate your profile by link in email.")


@pytest.mark.fixtures({"client": "client", "db": "db_empty"})
def test_create_new_user_successfully_creates_user_in_db_returns_200(fixtures):
    json = {
        "email": "str",
        "first_name": "str",
        "password": "str",
        "second_name": "str",
    }

    result = fixtures.client.post("/users/sign-up", json=json)

    assert result.status_code == 200
    created_user = fixtures.db.query(User).first()
    assert created_user.created_ts <= datetime.utcnow()
    assert created_user.email == json["email"]
    assert created_user.first_name == json["first_name"]
    assert created_user.is_active is False
    assert created_user.password == hashlib.sha256(json["password"].encode()).hexdigest()
    assert created_user.role == UserRole.regular
    assert created_user.second_name == json["second_name"]
    assert created_user.updated_ts <= datetime.utcnow()


@pytest.mark.fixtures({"client": "client", "db": "db_empty"})
def test_create_new_user_successfully_creates_activation_key_in_db_returns_200(fixtures):
    json = {
        "email": "str",
        "first_name": "str",
        "password": "str",
        "second_name": "str",
    }

    result = fixtures.client.post("/users/sign-up", json=json)

    assert result.status_code == 200
    created_user = fixtures.db.query(User).first()
    generated_key = fixtures.db.query(ActivationKey).first()
    assert generated_key.user_id == created_user.id
    assert isinstance(generated_key.key, uuid.UUID)


@pytest.mark.fixtures({"client": "client", "db": "db_empty"})
def test_activate_user_user_not_found_returns_404(fixtures):
    key = uuid.uuid4()

    result = fixtures.client.get(f"/users/activate/{key}")

    assert result.status_code == 404
    assert result.json()["detail"] == "User not found."


@pytest.mark.fixtures({"client": "client", "db": "db_with_activation_key"})
def test_activate_user_returns_correct_response(fixtures):
    key = "da7adade-dccd-4fa1-b37e-dd768310178e"

    result = fixtures.client.get(f"/users/activate/{key}")

    assert result.status_code == 200
    assert result.json()["message"] == "User's profile is active."


@pytest.mark.fixtures({"client": "client", "db": "db_with_activation_key"})
def test_activate_user_correct_changes_in_db(fixtures):
    key = "da7adade-dccd-4fa1-b37e-dd768310178e"

    result = fixtures.client.get(f"/users/activate/{key}")

    assert result.status_code == 200
    user = fixtures.db.query(User).first()
    assert user.is_active


@pytest.mark.fixtures({"client": "client", "db": "db_with_not_active_user"})
def test_login_user_by_not_active_user_returns_404(fixtures):
    json = {
        "email": "str",
        "password": "str",
    }

    result = fixtures.client.post("/users/sign-in", json=json)

    assert result.status_code == 404
    assert result.json()["detail"] == "User not found."


@pytest.mark.fixtures({"client": "client", "db": "db_with_admin_user"})
def test_login_user_with_not_correct_password_returns_400(fixtures):
    json = {
        "email": "str",
        "password": "str_",
    }

    result = fixtures.client.post("/users/sign-in", json=json)

    assert result.status_code == 400
    assert result.json()["detail"] == "Incorrect password."


@pytest.mark.fixtures({"client": "client", "db": "db_with_admin_user"})
def test_login_user_returns_correct_response(fixtures):
    json = {
        "email": "str",
        "password": "str",
    }

    result = fixtures.client.post("/users/sign-in", json=json)

    assert result.status_code == 200
    token = result.json()["token"]
    token_data = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
    assert token_data["id"] == 1
    assert token_data["role"] == UserRole.admin.value
    user = result.json()["user"]
    assert user["id"] == 1
    assert user["email"] == "str"
    assert user["first_name"] == "str"
    assert user["role"] == UserRole.admin.value
    assert user["second_name"] == "str"


@pytest.mark.fixtures({"client": "client", "db": "db_with_admin_and_regular_users"})
def test_get_user_with_no_token_returns_403(fixtures):
    result = fixtures.client.get("/users/1")

    assert result.status_code == 403
    assert result.json()["detail"] == "Not authenticated"


@pytest.mark.fixtures({"client": "client", "db": "db_with_admin_and_regular_users", "token": "regular_token"})
def test_get_user_by_regular_user_not_himself_returns_403(fixtures):
    result = fixtures.client.get("/users/1", headers={"Authorization": f"Bearer {fixtures.token}"})

    assert result.status_code == 403
    assert result.json()["detail"] == "No permissions."


@pytest.mark.fixtures({"client": "client", "db": "db_with_admin_and_regular_users", "token": "admin_token"})
def test_get_user_by_admin_user_not_found_returns_404(fixtures):
    result = fixtures.client.get("/users/3", headers={"Authorization": f"Bearer {fixtures.token}"})

    assert result.status_code == 404
    assert result.json()["detail"] == "User not found."


@pytest.mark.fixtures({"client": "client", "db": "db_with_admin_and_regular_users", "token": "admin_token"})
def test_get_user_by_admin_user_returns_correct_response(fixtures):
    result = fixtures.client.get("/users/2", headers={"Authorization": f"Bearer {fixtures.token}"})

    assert result.status_code == 200
    result_json = result.json()
    assert result_json["id"] == 2
    assert result_json["email"] == "str2"
    assert result_json["first_name"] == "str2"
    assert result_json["role"] == UserRole.regular.value
    assert result_json["second_name"] == "str2"
    path_to_file = Path("cache") / "2.json"
    assert path_to_file.exists()
    assert result_json == UserOut.parse_file(path_to_file).dict()
    path_to_file.unlink()


@pytest.mark.fixtures({"client": "client", "db": "db_with_admin_and_regular_users", "token": "regular_token"})
def test_get_user_by_regular_user_returns_correct_response(fixtures):
    result = fixtures.client.get("/users/2", headers={"Authorization": f"Bearer {fixtures.token}"})

    assert result.status_code == 200
    result_json = result.json()
    assert result_json["id"] == 2
    assert result_json["email"] == "str2"
    assert result_json["first_name"] == "str2"
    assert result_json["role"] == UserRole.regular.value
    assert result_json["second_name"] == "str2"
    path_to_file = Path("cache") / "2.json"
    assert path_to_file.exists()
    path_to_file.unlink()


@pytest.mark.fixtures({"client": "client", "db": "db_with_admin_and_regular_users", "token": "regular_token"})
def test_update_user_returns_correct_response(fixtures):
    json = {
        "first_name": "strstr",
    }

    result = fixtures.client.patch("/users/2", headers={"Authorization": f"Bearer {fixtures.token}"}, json=json)

    assert result.status_code == 200
    result_json = result.json()
    assert result_json["id"] == 2
    assert result_json["email"] == "str2"
    assert result_json["first_name"] == "strstr"
    assert result_json["role"] == UserRole.regular.value
    assert result_json["second_name"] == "str2"
