from datetime import datetime, timezone
from uuid import uuid4
import pytest
import requests

from app.models.calculation import Calculation


@pytest.fixture
def base_url(fastapi_server: str) -> str:
    return fastapi_server.rstrip("/")


def _parse_datetime(dt_str: str) -> datetime:
    if dt_str.endswith('Z'):
        dt_str = dt_str.replace('Z', '+00:00')
    return datetime.fromisoformat(dt_str)


def register_and_login(base_url: str, user_data: dict) -> dict:
    reg_url = f"{base_url}/auth/register"
    login_url = f"{base_url}/auth/login"

    reg_response = requests.post(reg_url, json=user_data)
    assert reg_response.status_code == 201

    login_payload = {
        "username": user_data["username"],
        "password": user_data["password"]
    }

    login_response = requests.post(login_url, json=login_payload)
    assert login_response.status_code == 200

    return login_response.json()


def test_health_endpoint(base_url: str):
    response = requests.get(f"{base_url}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_user_registration(base_url: str):
    payload = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice.smith@example.com",
        "username": "alicesmith",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }

    response = requests.post(f"{base_url}/auth/register", json=payload)
    assert response.status_code == 201

    data = response.json()
    for key in ["id", "username", "email", "first_name", "last_name", "is_active", "is_verified"]:
        assert key in data

    assert data["username"] == "alicesmith"
    assert data["email"] == "alice.smith@example.com"
    assert data["first_name"] == "Alice"
    assert data["last_name"] == "Smith"
    assert data["is_active"] is True
    assert data["is_verified"] is False


def test_user_login(base_url: str):
    user = {
        "first_name": "Bob",
        "last_name": "Jones",
        "email": "bob.jones@example.com",
        "username": "bobjones",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }

    requests.post(f"{base_url}/auth/register", json=user)

    login = requests.post(f"{base_url}/auth/login", json={
        "username": user["username"],
        "password": user["password"]
    })

    assert login.status_code == 200

    data = login.json()

    required = [
        "access_token", "refresh_token", "token_type", "expires_at",
        "user_id", "username", "email", "first_name", "last_name",
        "is_active", "is_verified"
    ]

    for field in required:
        assert field in data

    assert data["token_type"].lower() == "bearer"
    assert data["username"] == user["username"]
    assert data["email"] == user["email"]

    expires_at = _parse_datetime(data["expires_at"])
    assert expires_at > datetime.now(timezone.utc)


def test_create_calculation_addition(base_url: str):
    user = {
        "first_name": "Calc",
        "last_name": "Adder",
        "email": f"calc{uuid4()}@example.com",
        "username": f"user_{uuid4()}",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }

    token = register_and_login(base_url, user)["access_token"]

    response = requests.post(
        f"{base_url}/calculations",
        json={"type": "addition", "inputs": [10.5, 3, 2], "user_id": "ignored"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    assert response.json()["result"] == 15.5


def test_create_calculation_subtraction(base_url: str):
    user = {
        "first_name": "Calc",
        "last_name": "Sub",
        "email": f"calc{uuid4()}@example.com",
        "username": f"user_{uuid4()}",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }

    token = register_and_login(base_url, user)["access_token"]

    response = requests.post(
        f"{base_url}/calculations",
        json={"type": "subtraction", "inputs": [10, 3, 2], "user_id": "ignored"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    assert response.json()["result"] == 5


def test_create_calculation_multiplication(base_url: str):
    user = {
        "first_name": "Calc",
        "last_name": "Mult",
        "email": f"calc{uuid4()}@example.com",
        "username": f"user_{uuid4()}",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }

    token = register_and_login(base_url, user)["access_token"]

    response = requests.post(
        f"{base_url}/calculations",
        json={"type": "multiplication", "inputs": [2, 3, 4], "user_id": "ignored"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    assert response.json()["result"] == 24


def test_create_calculation_division(base_url: str):
    user = {
        "first_name": "Calc",
        "last_name": "Div",
        "email": f"calc{uuid4()}@example.com",
        "username": f"user_{uuid4()}",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!"
    }

    token = register_and_login(base_url, user)["access_token"]

    response = requests.post(
        f"{base_url}/calculations",
        json={"type": "division", "inputs": [100, 2, 5], "user_id": "ignored"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    assert response.json()["result"] == 10


def test_model_addition():
    calc = Calculation.create("addition", uuid4(), 1, 2)
    assert calc.get_result() == 3

def test_model_subtraction():
    calc = Calculation.create("subtraction", uuid4(), 10, 3)
    assert calc.get_result() == 7

def test_model_multiplication():
    calc = Calculation.create("multiplication", uuid4(), 2, 4)
    assert calc.get_result() == 8

def test_model_division():
    calc = Calculation.create("division", uuid4(), 100, 5)
    assert calc.get_result() == 20

    with pytest.raises(ValueError):
        Calculation.create("division", uuid4(), 10, 0).get_result()