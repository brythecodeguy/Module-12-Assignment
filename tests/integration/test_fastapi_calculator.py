# tests/integration/test_fastapi_calculator.py

import pytest  # Import the pytest framework for writing and running tests
from fastapi.testclient import TestClient  # Import TestClient for simulating API requests
from app.main import app  # Import the FastAPI app instance from your main application file
from types import SimpleNamespace
from fastapi import HTTPException
from datetime import datetime
from uuid import uuid4
from types import SimpleNamespace
import runpy
import warnings
from pydantic import ValidationError
from app import main as main_module

# ---------------------------------------------
# Pytest Fixture: client
# ---------------------------------------------

@pytest.fixture
def client():
    """
    Pytest Fixture to create a TestClient for the FastAPI application.

    This fixture initializes a TestClient instance that can be used to simulate
    requests to the FastAPI application without running a live server. The client
    is yielded to the test functions and properly closed after the tests complete.

    Benefits:
    - Speeds up testing by avoiding the overhead of running a server.
    - Allows for testing API endpoints in isolation.
    """
    with TestClient(app) as client:
        yield client  # Provide the TestClient instance to the test functions

# ---------------------------------------------
# Test Function: test_add_api
# ---------------------------------------------

def test_add_api(client):
    """
    Test the Addition API Endpoint.

    This test verifies that the `/add` endpoint correctly adds two numbers provided
    in the JSON payload and returns the expected result.

    Steps:
    1. Send a POST request to the `/add` endpoint with JSON data `{'a': 10, 'b': 5}`.
    2. Assert that the response status code is `200 OK`.
    3. Assert that the JSON response contains the correct result (`15`).
    """
    # Send a POST request to the '/add' endpoint with JSON payload
    response = client.post('/add', json={'a': 10, 'b': 5})
    
    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # Assert that the JSON response contains the correct 'result' value
    assert response.json()['result'] == 15, f"Expected result 15, got {response.json()['result']}"

# ---------------------------------------------
# Test Function: test_subtract_api
# ---------------------------------------------

def test_subtract_api(client):
    """
    Test the Subtraction API Endpoint.

    This test verifies that the `/subtract` endpoint correctly subtracts the second number
    from the first number provided in the JSON payload and returns the expected result.

    Steps:
    1. Send a POST request to the `/subtract` endpoint with JSON data `{'a': 10, 'b': 5}`.
    2. Assert that the response status code is `200 OK`.
    3. Assert that the JSON response contains the correct result (`5`).
    """
    # Send a POST request to the '/subtract' endpoint with JSON payload
    response = client.post('/subtract', json={'a': 10, 'b': 5})
    
    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # Assert that the JSON response contains the correct 'result' value
    assert response.json()['result'] == 5, f"Expected result 5, got {response.json()['result']}"

# ---------------------------------------------
# Test Function: test_multiply_api
# ---------------------------------------------

def test_multiply_api(client):
    """
    Test the Multiplication API Endpoint.

    This test verifies that the `/multiply` endpoint correctly multiplies two numbers
    provided in the JSON payload and returns the expected result.

    Steps:
    1. Send a POST request to the `/multiply` endpoint with JSON data `{'a': 10, 'b': 5}`.
    2. Assert that the response status code is `200 OK`.
    3. Assert that the JSON response contains the correct result (`50`).
    """
    # Send a POST request to the '/multiply' endpoint with JSON payload
    response = client.post('/multiply', json={'a': 10, 'b': 5})
    
    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # Assert that the JSON response contains the correct 'result' value
    assert response.json()['result'] == 50, f"Expected result 50, got {response.json()['result']}"

# ---------------------------------------------
# Test Function: test_divide_api
# ---------------------------------------------

def test_divide_api(client):
    """
    Test the Division API Endpoint.

    This test verifies that the `/divide` endpoint correctly divides the first number
    by the second number provided in the JSON payload and returns the expected result.

    Steps:
    1. Send a POST request to the `/divide` endpoint with JSON data `{'a': 10, 'b': 2}`.
    2. Assert that the response status code is `200 OK`.
    3. Assert that the JSON response contains the correct result (`5`).
    """
    # Send a POST request to the '/divide' endpoint with JSON payload
    response = client.post('/divide', json={'a': 10, 'b': 2})
    
    # Assert that the response status code is 200 (OK)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # Assert that the JSON response contains the correct 'result' value
    assert response.json()['result'] == 5, f"Expected result 5, got {response.json()['result']}"

# ---------------------------------------------
# Test Function: test_divide_by_zero_api
# ---------------------------------------------

def test_divide_by_zero_api(client):
    """
    Test the Division by Zero API Endpoint.

    This test verifies that the `/divide` endpoint correctly handles division by zero
    by returning an appropriate error message and status code.

    Steps:
    1. Send a POST request to the `/divide` endpoint with JSON data `{'a': 10, 'b': 0}`.
    2. Assert that the response status code is `400 Bad Request`.
    3. Assert that the JSON response contains an 'error' field with the message "Cannot divide by zero!".
    """
    # Send a POST request to the '/divide' endpoint with JSON payload attempting division by zero
    response = client.post('/divide', json={'a': 10, 'b': 0})
    
    # Assert that the response status code is 400 (Bad Request), indicating an error occurred
    assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
    
    # Assert that the JSON response contains an 'error' field
    assert 'error' in response.json(), "Response JSON does not contain 'error' field"
    
    # Assert that the 'error' field contains the correct error message
    assert "Cannot divide by zero!" in response.json()['error'], \
        f"Expected error message 'Cannot divide by zero!', got '{response.json()['error']}'"

# ---------------------------------------------
# Additional Coverage Tests
# ---------------------------------------------

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_add_invalid_payload(client):
    response = client.post("/add", json={"a": "bad", "b": 2})
    assert response.status_code == 400
    assert "error" in response.json()


def test_divide_internal_error(monkeypatch, client):
    def fake_divide(a, b):
        raise Exception("boom")

    monkeypatch.setattr("app.main.divide", fake_divide)

    response = client.post("/divide", json={"a": 10, "b": 2})
    assert response.status_code == 500


def test_register_value_error(client):
    payload = {
        "first_name": "A",
        "last_name": "B",
        "email": "bademail",
        "username": "testuser",
        "password": "short",
        "confirm_password": "short"
    }

    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400


def test_login_invalid(client):
    response = client.post("/auth/login", json={
        "username": "wrong",
        "password": "wrong"
    })
    assert response.status_code == 400


# ---------------------------------------------
# AUTH REQUIRED ROUTES (reuse existing login flow)
# ---------------------------------------------

def get_auth_headers(client):
    register_payload = {
        "first_name": "Test",
        "last_name": "User",
        "email": "testuser@example.com",
        "username": "testuser123",
        "password": "GoodPass123!",
        "confirm_password": "GoodPass123!"
    }

    client.post("/auth/register", json=register_payload)

    login_response = client.post("/auth/login", json={
        "username": "testuser123",
        "password": "GoodPass123!"
    })

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_read_calculation_not_found(client):
    headers = get_auth_headers(client)
    fake_id = "11111111-1111-1111-1111-111111111111"

    response = client.get(f"/calculations/{fake_id}", headers=headers)
    assert response.status_code == 404


def test_update_calculation_not_found(client):
    headers = get_auth_headers(client)
    fake_id = "11111111-1111-1111-1111-111111111111"

    response = client.put(
        f"/calculations/{fake_id}",
        json={"type": "addition", "a": 1, "b": 2},
        headers=headers
    )

    assert response.status_code == 404


def test_delete_calculation_not_found(client):
    headers = get_auth_headers(client)
    fake_id = "11111111-1111-1111-1111-111111111111"

    response = client.delete(f"/calculations/{fake_id}", headers=headers)
    assert response.status_code == 404


def test_add_internal_error(monkeypatch, client):
    def fake_add(a, b):
        raise Exception("boom")

    monkeypatch.setattr("app.main.add", fake_add)

    response = client.post("/add", json={"a": 1, "b": 2})
    assert response.status_code == 400


def test_validation_handler_trigger(client):
    response = client.post("/add", json={"a": "string", "b": "string"})
    assert response.status_code == 400
    assert "error" in response.json()


def test_login_form_invalid_direct(monkeypatch):
    def fake_authenticate(db, username, password):
        return None  # force invalid login

    monkeypatch.setattr(main_module.User, "authenticate", fake_authenticate)

    class FakeForm:
        username = "baduser"
        password = "GoodPass123!"

    class FakeDB:
        pass

    with pytest.raises(HTTPException) as exc_info:
        main_module.login_form(FakeForm(), FakeDB())

    assert exc_info.value.status_code == 401


def test_login_json_fallback_expires_at(monkeypatch):
    def fake_authenticate(db, username, password):
        return {
            "access_token": "abc",
            "refresh_token": "def",
            "user_id": str(uuid4()),
            "username": "user1",
            "email": "user1@example.com",
            "first_name": "User",
            "last_name": "One",
            "is_active": True,
            "is_verified": False,
        }

    monkeypatch.setattr(main_module.User, "authenticate", fake_authenticate)

    class FakeDB:
        def commit(self): pass 

    login = main_module.UserLogin(username="user1", password="GoodPass123!")
    result = main_module.login_json(login, db=FakeDB())

    assert result.access_token == "abc"
    assert result.refresh_token == "def"
    assert result.token_type == "bearer"
    assert result.expires_at is not None

def test_register_unexpected_exception(monkeypatch):
    class FakeDB:
        def rollback(self):
            self.rolled_back = True

    def fake_register(db, user_data):
        raise Exception("boom")

    monkeypatch.setattr(main_module.User, "register", fake_register)

    user = main_module.UserCreate(
        first_name="A",
        last_name="B",
        email="ab@example.com",
        username="abuser",
        password="GoodPass123!",
        confirm_password="GoodPass123!",
    )

    with pytest.raises(HTTPException) as exc_info:
        main_module.register(user, db=FakeDB())

    assert exc_info.value.status_code == 500


def test_create_calculation_success_direct(monkeypatch):
    fake_calc = SimpleNamespace(
        id="1",
        user_id="u1",
        type="addition",
        a=1,
        b=2,
        result=3,
        created_at=None,
        updated_at=None,
    )

    class FakeDB:
        def add(self, obj): pass
        def commit(self): pass
        def refresh(self, obj): pass

    monkeypatch.setattr(main_module.Calculation, "create", lambda **kwargs: fake_calc)
    monkeypatch.setattr(main_module.CalculationRead, "model_validate", lambda obj: obj)

    user = SimpleNamespace(id="u1")
    result = main_module.create_calculation(
        main_module.CalculationCreate(type="addition", a=1, b=2),
        db=FakeDB(),
        current_user=user,
    )

    assert result.result == 3


def test_create_calculation_value_error_direct(monkeypatch):
    class FakeDB:
        def rollback(self): pass

    def fake_create(**kwargs):
        raise ValueError("bad calc")

    monkeypatch.setattr(main_module.Calculation, "create", fake_create)

    user = SimpleNamespace(id="u1")

    with pytest.raises(HTTPException) as exc_info:
        main_module.create_calculation(
            main_module.CalculationCreate(type="addition", a=1, b=2),
            db=FakeDB(),
            current_user=user,
        )

    assert exc_info.value.status_code == 400


def test_browse_calculations_direct(monkeypatch):
    fake_calc = SimpleNamespace(
        id="1",
        user_id="u1",
        type="addition",
        a=1,
        b=2,
        result=3,
        created_at=None,
        updated_at=None,
    )

    class FakeQuery:
        def filter(self, *args, **kwargs): return self
        def order_by(self, *args, **kwargs): return self
        def all(self): return [fake_calc]

    class FakeDB:
        def query(self, model): return FakeQuery()

    monkeypatch.setattr(main_module.CalculationRead, "model_validate", lambda obj: obj)

    result = main_module.browse_calculations(
        db=FakeDB(),
        current_user=SimpleNamespace(id="u1"),
    )

    assert len(result) == 1
    assert result[0].result == 3


def test_read_calculation_success_direct(monkeypatch):
    fake_calc = SimpleNamespace(
        id="1",
        user_id="u1",
        type="addition",
        a=1,
        b=2,
        result=3,
        created_at=None,
        updated_at=None,
    )

    class FakeQuery:
        def filter(self, *args, **kwargs): return self
        def first(self): return fake_calc

    class FakeDB:
        def query(self, model): return FakeQuery()

    monkeypatch.setattr(main_module.CalculationRead, "model_validate", lambda obj: obj)

    result = main_module.read_calculation(
        calculation_id="11111111-1111-1111-1111-111111111111",
        db=FakeDB(),
        current_user=SimpleNamespace(id="u1"),
    )

    assert result.result == 3


def test_update_calculation_success_direct(monkeypatch):
    fake_existing = SimpleNamespace(
        id="1",
        user_id="u1",
        type="addition",
        a=1,
        b=2,
        result=3,
        created_at=None,
        updated_at=None,
    )

    fake_updated = SimpleNamespace(type="subtraction", a=5, b=2, result=3)

    class FakeQuery:
        def filter(self, *args, **kwargs): return self
        def first(self): return fake_existing

    class FakeDB:
        def query(self, model): return FakeQuery()
        def commit(self): pass
        def refresh(self, obj): pass
        def rollback(self): pass

    monkeypatch.setattr(main_module.Calculation, "create", lambda **kwargs: fake_updated)
    monkeypatch.setattr(main_module.CalculationRead, "model_validate", lambda obj: obj)

    result = main_module.update_calculation(
        calculation_id="11111111-1111-1111-1111-111111111111",
        calculation_update=main_module.CalculationUpdate(type="subtraction", a=5, b=2),
        db=FakeDB(),
        current_user=SimpleNamespace(id="u1"),
    )

    assert result.type == "subtraction"
    assert result.a == 5
    assert result.b == 2


def test_update_calculation_value_error_direct(monkeypatch):
    fake_existing = SimpleNamespace(
        id="1",
        user_id="u1",
        type="addition",
        a=1,
        b=2,
        result=3,
    )

    class FakeQuery:
        def filter(self, *args, **kwargs): return self
        def first(self): return fake_existing

    class FakeDB:
        def query(self, model): return FakeQuery()
        def rollback(self): pass

    def fake_create(**kwargs):
        raise ValueError("bad update")

    monkeypatch.setattr(main_module.Calculation, "create", fake_create)

    with pytest.raises(HTTPException) as exc_info:
        main_module.update_calculation(
            calculation_id="11111111-1111-1111-1111-111111111111",
            calculation_update=main_module.CalculationUpdate(type="addition", a=1, b=2),
            db=FakeDB(),
            current_user=SimpleNamespace(id="u1"),
        )

    assert exc_info.value.status_code == 400


def test_delete_calculation_success_direct():
    fake_existing = SimpleNamespace(id="1")

    class FakeQuery:
        def filter(self, *args, **kwargs): return self
        def first(self): return fake_existing

    class FakeDB:
        def query(self, model): return FakeQuery()
        def delete(self, obj): self.deleted = obj
        def commit(self): pass

    db = FakeDB()

    result = main_module.delete_calculation(
        calculation_id="11111111-1111-1111-1111-111111111111",
        db=db,
        current_user=SimpleNamespace(id="u1"),
    )

    assert db.deleted is fake_existing
    assert result is None

def test_root_route(client):
    response = client.get("/")
    assert response.status_code == 200


def test_subtract_internal_error(monkeypatch, client):
    def fake_subtract(a, b):
        raise Exception("boom")

    monkeypatch.setattr("app.main.subtract", fake_subtract)

    response = client.post("/subtract", json={"a": 10, "b": 2})
    assert response.status_code == 400


def test_multiply_internal_error(monkeypatch, client):
    def fake_multiply(a, b):
        raise Exception("boom")

    monkeypatch.setattr("app.main.multiply", fake_multiply)

    response = client.post("/multiply", json={"a": 10, "b": 2})
    assert response.status_code == 400


def test_login_json_invalid_direct(monkeypatch):
    def fake_authenticate(db, username, password):
        return None

    monkeypatch.setattr(main_module.User, "authenticate", fake_authenticate)

    class FakeDB:
        def commit(self):
            pass

    login = main_module.UserLogin(username="user1", password="GoodPass123!")

    with pytest.raises(HTTPException) as exc_info:
        main_module.login_json(login, db=FakeDB())

    assert exc_info.value.status_code == 401


def test_login_json_naive_expires_at(monkeypatch):
    def fake_authenticate(db, username, password):
        return {
            "access_token": "abc",
            "refresh_token": "def",
            "user_id": str(uuid4()),
            "username": "user1",
            "email": "user1@example.com",
            "first_name": "User",
            "last_name": "One",
            "is_active": True,
            "is_verified": False,
            "expires_at": datetime.now(),  # naive datetime branch
        }

    monkeypatch.setattr(main_module.User, "authenticate", fake_authenticate)

    class FakeDB:
        def commit(self):
            pass

    login = main_module.UserLogin(username="user1", password="GoodPass123!")
    result = main_module.login_json(login, db=FakeDB())

    assert result.expires_at.tzinfo is not None


def test_login_form_success_direct(monkeypatch):
    def fake_authenticate(db, username, password):
        return {"access_token": "abc"}

    monkeypatch.setattr(main_module.User, "authenticate", fake_authenticate)

    class FakeForm:
        username = "user1"
        password = "GoodPass123!"

    result = main_module.login_form(FakeForm(), db=object())

    assert result["access_token"] == "abc"
    assert result["token_type"] == "bearer"


def test_read_calculation_not_found_direct():
    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return None

    class FakeDB:
        def query(self, model):
            return FakeQuery()

    with pytest.raises(HTTPException) as exc_info:
        main_module.read_calculation(
            calculation_id=uuid4(),
            db=FakeDB(),
            current_user=SimpleNamespace(id=uuid4()),
        )

    assert exc_info.value.status_code == 404


def test_delete_calculation_not_found_direct():
    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return None

    class FakeDB:
        def query(self, model):
            return FakeQuery()

    with pytest.raises(HTTPException) as exc_info:
        main_module.delete_calculation(
            calculation_id=uuid4(),
            db=FakeDB(),
            current_user=SimpleNamespace(id=uuid4()),
        )

    assert exc_info.value.status_code == 404


def test_dunder_main_runs_uvicorn(monkeypatch):
    # warning suppression
    called = {}

    def fake_run(app, host, port):
        called["host"] = host
        called["port"] = port

    monkeypatch.setattr("uvicorn.run", fake_run)

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=r".*found in sys\.modules.*prior to execution of 'app\.main'.*",
            category=RuntimeWarning,
        )
        runpy.run_module("app.main", run_name="__main__")

    assert called["host"] == "127.0.0.1"
    assert called["port"] == 8000


def test_operation_request_validator_direct_raises_value_error():
    with pytest.raises(ValueError, match="Both a and b must be numbers."):
        main_module.OperationRequest.validate_numbers("not-a-number")


def test_create_calculation_internal_error_direct(monkeypatch):
    class FakeDB:
        def add(self, obj):
            pass

        def commit(self):
            raise Exception("db boom")

        def refresh(self, obj):
            pass

        def rollback(self):
            pass

    fake_calc = SimpleNamespace(
        id=uuid4(),
        user_id=uuid4(),
        type="addition",
        a=1,
        b=2,
        result=3,
        created_at=None,
        updated_at=None,
    )

    monkeypatch.setattr(main_module.Calculation, "create", lambda **kwargs: fake_calc)

    with pytest.raises(HTTPException) as exc_info:
        main_module.create_calculation(
            main_module.CalculationCreate(type="addition", a=1, b=2),
            db=FakeDB(),
            current_user=SimpleNamespace(id=uuid4()),
        )

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal Server Error"


def test_update_calculation_internal_error_direct(monkeypatch):
    fake_existing = SimpleNamespace(
        id=uuid4(),
        user_id=uuid4(),
        type="addition",
        a=1,
        b=2,
        result=3,
        created_at=None,
        updated_at=None,
    )

    fake_updated = SimpleNamespace(type="subtraction", a=5, b=2, result=3)

    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return fake_existing

    class FakeDB:
        def query(self, model):
            return FakeQuery()

        def commit(self):
            raise Exception("db boom")

        def refresh(self, obj):
            pass

        def rollback(self):
            pass

    monkeypatch.setattr(main_module.Calculation, "create", lambda **kwargs: fake_updated)

    with pytest.raises(HTTPException) as exc_info:
        main_module.update_calculation(
            calculation_id=uuid4(),
            calculation_update=main_module.CalculationUpdate(type="subtraction", a=5, b=2),
            db=FakeDB(),
            current_user=SimpleNamespace(id=uuid4()),
        )

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal Server Error"