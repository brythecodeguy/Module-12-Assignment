from datetime import datetime, timezone
from uuid import uuid4
import pytest
import requests

from app.models.calculation import Calculation


@pytest.fixture
def base_url(fastapi_server: str) -> str:
    return fastapi_server.rstrip("/")


def _parse_datetime(dt_str: str) -> datetime:
    if dt_str.endswith("Z"):
        dt_str = dt_str.replace("Z", "+00:00")
    return datetime.fromisoformat(dt_str)


def register_and_login(base_url: str, user_data: dict) -> dict:
    reg_url = f"{base_url}/users/register"
    login_url = f"{base_url}/users/login"

    reg_response = requests.post(reg_url, json=user_data)
    assert reg_response.status_code == 201, f"User registration failed: {reg_response.text}"

    login_payload = {
        "username": user_data["username"],
        "password": user_data["password"],
    }
    login_response = requests.post(login_url, json=login_payload)
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"

    return login_response.json()


def test_health_endpoint(base_url: str):
    response = requests.get(f"{base_url}/health")
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}. Response: {response.text}"
    assert response.json() == {"status": "ok"}


def test_user_registration(base_url: str):
    payload = {
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice.smith@example.com",
        "username": "alicesmith",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    }

    response = requests.post(f"{base_url}/users/register", json=payload)
    assert response.status_code == 201, f"Expected 201 but got {response.status_code}. Response: {response.text}"

    data = response.json()
    for key in ["id", "username", "email", "first_name", "last_name", "is_active", "is_verified"]:
        assert key in data, f"Field '{key}' missing in registration response."

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
        "confirm_password": "SecurePass123!",
    }

    reg_response = requests.post(f"{base_url}/users/register", json=user)
    assert reg_response.status_code == 201, f"User registration failed: {reg_response.text}"

    login = requests.post(
        f"{base_url}/users/login",
        json={
            "username": user["username"],
            "password": user["password"],
        },
    )
    assert login.status_code == 200, f"Login failed: {login.text}"

    data = login.json()

    required = {
        "access_token": str,
        "refresh_token": str,
        "token_type": str,
        "expires_at": str,
        "user_id": str,
        "username": str,
        "email": str,
        "first_name": str,
        "last_name": str,
        "is_active": bool,
        "is_verified": bool,
    }

    for field, expected_type in required.items():
        assert field in data, f"Missing field: {field}"
        assert isinstance(data[field], expected_type), f"Field {field} has wrong type. Expected {expected_type}, got {type(data[field])}"

    assert data["token_type"].lower() == "bearer"
    assert len(data["access_token"]) > 0
    assert len(data["refresh_token"]) > 0
    assert data["username"] == user["username"]
    assert data["email"] == user["email"]

    expires_at = _parse_datetime(data["expires_at"])
    assert expires_at > datetime.now(timezone.utc)


def test_create_calculation_addition(base_url: str):
    user = {
        "first_name": "Calc",
        "last_name": "Adder",
        "email": f"calc.adder{uuid4()}@example.com",
        "username": f"calc_adder_{uuid4()}",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    }

    token = register_and_login(base_url, user)["access_token"]

    response = requests.post(
        f"{base_url}/calculations",
        json={"type": "addition", "a": 10.5, "b": 3},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201, f"Addition calculation creation failed: {response.text}"
    assert response.json()["result"] == 13.5


def test_create_calculation_subtraction(base_url: str):
    user = {
        "first_name": "Calc",
        "last_name": "Subtractor",
        "email": f"calc.sub{uuid4()}@example.com",
        "username": f"calc_sub_{uuid4()}",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    }

    token = register_and_login(base_url, user)["access_token"]

    response = requests.post(
        f"{base_url}/calculations",
        json={"type": "subtraction", "a": 10, "b": 3},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201, f"Subtraction calculation creation failed: {response.text}"
    assert response.json()["result"] == 7


def test_create_calculation_multiplication(base_url: str):
    user = {
        "first_name": "Calc",
        "last_name": "Multiplier",
        "email": f"calc.mult{uuid4()}@example.com",
        "username": f"calc_mult_{uuid4()}",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    }

    token = register_and_login(base_url, user)["access_token"]

    response = requests.post(
        f"{base_url}/calculations",
        json={"type": "multiplication", "a": 2, "b": 3},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201, f"Multiplication calculation creation failed: {response.text}"
    assert response.json()["result"] == 6


def test_create_calculation_division(base_url: str):
    user = {
        "first_name": "Calc",
        "last_name": "Divider",
        "email": f"calc.div{uuid4()}@example.com",
        "username": f"calc_div_{uuid4()}",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    }

    token = register_and_login(base_url, user)["access_token"]

    response = requests.post(
        f"{base_url}/calculations",
        json={"type": "division", "a": 100, "b": 5},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201, f"Division calculation creation failed: {response.text}"
    assert response.json()["result"] == 20


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