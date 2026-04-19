# tests/integration/test_user_auth.py
import pytest
import asyncio
from app.models.user import User

from datetime import timedelta
from uuid import uuid4
from types import SimpleNamespace
from fastapi import HTTPException
from app.auth import jwt as jwt_module
from app.schemas.token import TokenType
from app.schemas.user import UserCreate

def test_password_hashing(db_session, fake_user_data):
    original_password = "TestPass123!"
    hashed = User.hash_password(original_password)

    user = User(
        first_name=fake_user_data["first_name"],
        last_name=fake_user_data["last_name"],
        email=fake_user_data["email"],
        username=fake_user_data["username"],
        password=hashed
    )

    assert user.verify_password(original_password) is True
    assert user.verify_password("WrongPass123!") is False
    assert hashed != original_password


def test_user_registration(db_session, fake_user_data):
    fake_user_data["password"] = "TestPass123!"
    fake_user_data["confirm_password"] = "TestPass123!"

    user = User.register(db_session, fake_user_data)
    db_session.commit()

    assert user.first_name == fake_user_data["first_name"]
    assert user.last_name == fake_user_data["last_name"]
    assert user.email == fake_user_data["email"]
    assert user.username == fake_user_data["username"]
    assert user.is_active is True
    assert user.is_verified is False
    assert user.verify_password("TestPass123!") is True


def test_duplicate_user_registration(db_session):
    user1_data = {
        "first_name": "Test",
        "last_name": "User1",
        "email": "unique.test@example.com",
        "username": "uniqueuser1",
        "password": "TestPass123!",
        "confirm_password": "TestPass123!"
    }

    user2_data = {
        "first_name": "Test",
        "last_name": "User2",
        "email": "unique.test@example.com",
        "username": "uniqueuser2",
        "password": "TestPass123!",
        "confirm_password": "TestPass123!"
    }

    first_user = User.register(db_session, user1_data)
    db_session.commit()
    db_session.refresh(first_user)

    with pytest.raises(ValueError, match="Username or email already exists"):
        User.register(db_session, user2_data)


def test_user_authentication(db_session, fake_user_data):
    fake_user_data["password"] = "TestPass123!"
    fake_user_data["confirm_password"] = "TestPass123!"
    user = User.register(db_session, fake_user_data)
    db_session.commit()

    auth_result = User.authenticate(
        db_session,
        fake_user_data["username"],
        "TestPass123!"
    )

    assert auth_result is not None
    assert "access_token" in auth_result
    assert "refresh_token" in auth_result
    assert "token_type" in auth_result
    assert auth_result["token_type"] == "bearer"
    assert "user_id" in auth_result
    assert auth_result["user_id"] == user.id
    assert auth_result["username"] == user.username
    assert auth_result["email"] == user.email


def test_user_last_login_update(db_session, fake_user_data):
    fake_user_data["password"] = "TestPass123!"
    fake_user_data["confirm_password"] = "TestPass123!"
    user = User.register(db_session, fake_user_data)
    db_session.commit()

    assert user.last_login is None
    User.authenticate(db_session, fake_user_data["username"], "TestPass123!")
    db_session.refresh(user)
    assert user.last_login is not None


def test_unique_email_username(db_session):
    user1_data = {
        "first_name": "Test",
        "last_name": "User1",
        "email": "unique_test@example.com",
        "username": "uniqueuser",
        "password": "TestPass123!",
        "confirm_password": "TestPass123!"
    }

    User.register(db_session, user1_data)
    db_session.commit()

    user2_data = {
        "first_name": "Test",
        "last_name": "User2",
        "email": "unique_test@example.com",
        "username": "differentuser",
        "password": "TestPass123!",
        "confirm_password": "TestPass123!"
    }

    with pytest.raises(ValueError, match="Username or email already exists"):
        User.register(db_session, user2_data)


def test_short_password_registration(db_session):
    test_data = {
        "first_name": "Password",
        "last_name": "Test",
        "email": "short.pass@example.com",
        "username": "shortpass",
        "password": "Shor1!",
        "confirm_password": "Shor1!"
    }

    with pytest.raises(ValueError, match="Password must be at least 8 characters long"):
        User.register(db_session, test_data)


def test_invalid_token():
    invalid_token = "invalid.token.string"
    result = User.verify_token(invalid_token)
    assert result is None


def test_token_creation_and_verification(db_session, fake_user_data):
    fake_user_data["password"] = "TestPass123!"
    fake_user_data["confirm_password"] = "TestPass123!"
    user = User.register(db_session, fake_user_data)
    db_session.commit()

    token = User.create_access_token({"sub": str(user.id)})
    decoded_user_id = User.verify_token(token)
    assert decoded_user_id == user.id


def test_authenticate_with_email(db_session, fake_user_data):
    fake_user_data["password"] = "TestPass123!"
    fake_user_data["confirm_password"] = "TestPass123!"
    User.register(db_session, fake_user_data)
    db_session.commit()

    auth_result = User.authenticate(
        db_session,
        fake_user_data["email"],
        "TestPass123!"
    )

    assert auth_result is not None
    assert "access_token" in auth_result


def test_user_model_representation(test_user):
    expected = f"<User(name={test_user.first_name} {test_user.last_name}, email={test_user.email})>"
    assert str(test_user) == expected


def test_missing_password_registration(db_session):
    test_data = {
        "first_name": "NoPassword",
        "last_name": "Test",
        "email": "no.password@example.com",
        "username": "nopassworduser",
    }

    with pytest.raises(ValueError, match="Password must be at least 8 characters long"):
        User.register(db_session, test_data)


def test_register_invalid_email_raises_value_error(db_session):
    bad_user_data = {
        "first_name": "Bad",
        "last_name": "Email",
        "email": "not-an-email",
        "username": "bademailuser",
        "password": "GoodPass123!",
        "confirm_password": "GoodPass123!"
    }

    with pytest.raises(ValueError):
        User.register(db_session, bad_user_data)


def test_authenticate_invalid_password_returns_none(db_session, fake_user_data):
    fake_user_data["password"] = "TestPass123!"
    fake_user_data["confirm_password"] = "TestPass123!"
    User.register(db_session, fake_user_data)
    db_session.commit()

    result = User.authenticate(db_session, fake_user_data["username"], "WrongPass123!")
    assert result is None

def test_jwt_verify_password_success():
    password = "TestPass123!"
    hashed = jwt_module.get_password_hash(password)
    assert jwt_module.verify_password(password, hashed) is True


def test_jwt_verify_password_failure():
    password = "TestPass123!"
    hashed = jwt_module.get_password_hash(password)
    assert jwt_module.verify_password("WrongPass123!", hashed) is False


def test_create_access_token():
    token = jwt_module.create_token("123", TokenType.ACCESS)
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_refresh_token():
    token = jwt_module.create_token("123", TokenType.REFRESH)
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_token_with_uuid():
    token = jwt_module.create_token(uuid4(), TokenType.ACCESS)
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_token_with_custom_expiry():
    token = jwt_module.create_token("123", TokenType.ACCESS, expires_delta=timedelta(minutes=5))
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_token_encode_failure(monkeypatch):
    def fake_encode(*args, **kwargs):
        raise Exception("encode failed")

    monkeypatch.setattr(jwt_module.jwt, "encode", fake_encode)

    with pytest.raises(HTTPException) as exc_info:
        jwt_module.create_token("123", TokenType.ACCESS)

    assert exc_info.value.status_code == 500
    assert "Could not create token" in exc_info.value.detail


def test_decode_token_success(monkeypatch):
    token = jwt_module.create_token("123", TokenType.ACCESS)

    async def fake_is_blacklisted(jti):
        return False

    monkeypatch.setattr(jwt_module, "is_blacklisted", fake_is_blacklisted)

    payload = asyncio.run(jwt_module.decode_token(token, TokenType.ACCESS))

    assert payload["sub"] == "123"
    assert payload["type"] == TokenType.ACCESS.value
    assert "jti" in payload


def test_decode_token_invalid_type(monkeypatch):
    token = jwt_module.create_token("123", TokenType.REFRESH)

    async def fake_is_blacklisted(jti):
        return False

    monkeypatch.setattr(jwt_module, "is_blacklisted", fake_is_blacklisted)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(jwt_module.decode_token(token, TokenType.ACCESS))

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"


def test_decode_token_blacklisted(monkeypatch):
    token = jwt_module.create_token("123", TokenType.ACCESS)

    async def fake_is_blacklisted(jti):
        return True

    monkeypatch.setattr(jwt_module, "is_blacklisted", fake_is_blacklisted)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(jwt_module.decode_token(token, TokenType.ACCESS))

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token has been revoked"


def test_decode_token_expired(monkeypatch):
    token = jwt_module.create_token(
        "123",
        TokenType.ACCESS,
        expires_delta=timedelta(seconds=-1)
    )

    async def fake_is_blacklisted(jti):
        return False

    monkeypatch.setattr(jwt_module, "is_blacklisted", fake_is_blacklisted)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(jwt_module.decode_token(token, TokenType.ACCESS))

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token has expired"


def test_decode_token_invalid_token(monkeypatch):
    async def fake_is_blacklisted(jti):
        return False

    monkeypatch.setattr(jwt_module, "is_blacklisted", fake_is_blacklisted)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(jwt_module.decode_token("not.a.real.token", TokenType.ACCESS))

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"

# -----------------------
# REDIS TESTS
# -----------------------

class FakeRedis:
    def __init__(self):
        self.store = {}

    async def set(self, key, value, ex=None):
        self.store[key] = value

    async def exists(self, key):
        return 1 if key in self.store else 0


def test_add_to_blacklist(monkeypatch):
    from app.auth import redis as redis_module
    import asyncio

    fake = FakeRedis()

    async def fake_get_redis():
        return fake

    monkeypatch.setattr(redis_module, "get_redis", fake_get_redis)

    asyncio.run(redis_module.add_to_blacklist("abc123", 60))

    assert "blacklist:abc123" in fake.store


def test_is_blacklisted_true(monkeypatch):
    from app.auth import redis as redis_module
    import asyncio

    fake = FakeRedis()
    fake.store["blacklist:abc123"] = "1"

    async def fake_get_redis():
        return fake

    monkeypatch.setattr(redis_module, "get_redis", fake_get_redis)

    result = asyncio.run(redis_module.is_blacklisted("abc123"))

    assert result == 1


def test_is_blacklisted_false(monkeypatch):
    from app.auth import redis as redis_module
    import asyncio

    fake = FakeRedis()

    async def fake_get_redis():
        return fake

    monkeypatch.setattr(redis_module, "get_redis", fake_get_redis)

    result = asyncio.run(redis_module.is_blacklisted("abc123"))

    assert result == 0

def test_get_redis_caches_instance(monkeypatch):
    from app.auth import redis as redis_module
    import asyncio

    class FakeRedis:
        pass

    fake_instance = FakeRedis()

    async def fake_from_url(url):
        return fake_instance

    if hasattr(redis_module.get_redis, "redis"):
        delattr(redis_module.get_redis, "redis")

    monkeypatch.setattr(redis_module.aioredis, "from_url", fake_from_url)

    first = asyncio.run(redis_module.get_redis())
    second = asyncio.run(redis_module.get_redis())

    assert first is fake_instance
    assert second is fake_instance

def test_jwt_get_current_user_success(monkeypatch):
    async def fake_decode_token(token, token_type, verify_exp=True):
        return {"sub": "123"}

    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return SimpleNamespace(id="123", is_active=True)

    class FakeDB:
        def query(self, model):
            return FakeQuery()

    monkeypatch.setattr(jwt_module, "decode_token", fake_decode_token)

    user = asyncio.run(jwt_module.get_current_user(token="abc", db=FakeDB()))
    assert user.id == "123"
    assert user.is_active is True


def test_jwt_get_current_user_not_found(monkeypatch):
    async def fake_decode_token(token, token_type, verify_exp=True):
        return {"sub": "123"}

    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return None

    class FakeDB:
        def query(self, model):
            return FakeQuery()

    monkeypatch.setattr(jwt_module, "decode_token", fake_decode_token)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(jwt_module.get_current_user(token="abc", db=FakeDB()))

    assert exc_info.value.status_code == 401
    assert "User not found" in exc_info.value.detail


def test_jwt_get_current_user_inactive(monkeypatch):
    async def fake_decode_token(token, token_type, verify_exp=True):
        return {"sub": "123"}

    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return SimpleNamespace(id="123", is_active=False)

    class FakeDB:
        def query(self, model):
            return FakeQuery()

    monkeypatch.setattr(jwt_module, "decode_token", fake_decode_token)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(jwt_module.get_current_user(token="abc", db=FakeDB()))

    assert exc_info.value.status_code == 401
    assert "Inactive user" in exc_info.value.detail


def test_jwt_get_current_user_decode_failure(monkeypatch):
    async def fake_decode_token(token, token_type, verify_exp=True):
        raise Exception("bad token")

    class FakeDB:
        def query(self, model):
            return None

    monkeypatch.setattr(jwt_module, "decode_token", fake_decode_token)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(jwt_module.get_current_user(token="abc", db=FakeDB()))

    assert exc_info.value.status_code == 401
    assert "bad token" in exc_info.value.detail


def test_decode_token_verify_exp_false(monkeypatch):
    token = jwt_module.create_token(
        "123",
        TokenType.ACCESS,
        expires_delta=timedelta(seconds=-1)
    )

    async def fake_is_blacklisted(jti):
        return False

    monkeypatch.setattr(jwt_module, "is_blacklisted", fake_is_blacklisted)

    payload = asyncio.run(jwt_module.decode_token(token, TokenType.ACCESS, verify_exp=False))
    assert payload["sub"] == "123"

def test_decode_token_invalid_type_branch(monkeypatch):
    async def fake_is_blacklisted(jti):
        return False

    def fake_decode(token, secret, algorithms, options):
        return {
            "sub": "123",
            "type": TokenType.REFRESH.value,  # wrong type on purpose
            "jti": "abc123",
        }

    monkeypatch.setattr(jwt_module, "is_blacklisted", fake_is_blacklisted)
    monkeypatch.setattr(jwt_module.jwt, "decode", fake_decode)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(jwt_module.decode_token("fake-token", TokenType.ACCESS))

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token type"

def test_user_hashed_password_property(test_user):
    assert test_user.hashed_password == test_user.password


def test_user_register_with_schema_object(db_session):
    user_data = UserCreate(
        first_name="Schema",
        last_name="User",
        email="schema.user@example.com",
        username="schemauser",
        password="GoodPass123!",
        confirm_password="GoodPass123!"
    )

    user = User.register(db_session, user_data)

    assert user.email == "schema.user@example.com"
    assert user.username == "schemauser"
    assert user.verify_password("GoodPass123!") is True


def test_user_authenticate_updates_last_login_and_flushes(db_session, fake_user_data, monkeypatch):
    fake_user_data["password"] = "TestPass123!"
    fake_user_data["confirm_password"] = "TestPass123!"
    user = User.register(db_session, fake_user_data)
    db_session.refresh(user)

    called = {"flushed": False}

    original_flush = db_session.flush

    def fake_flush():
        called["flushed"] = True
        return original_flush()

    monkeypatch.setattr(db_session, "flush", fake_flush)

    result = User.authenticate(db_session, fake_user_data["username"], "TestPass123!")

    assert result is not None
    assert called["flushed"] is True
    assert user.last_login is not None


def test_user_create_access_and_refresh_token_helpers(test_user):
    access = User.create_access_token({"sub": str(test_user.id)})
    refresh = User.create_refresh_token({"sub": str(test_user.id)})

    assert isinstance(access, str)
    assert isinstance(refresh, str)
    assert len(access) > 0
    assert len(refresh) > 0

def test_user_register_with_schema_object_short_password_raises(db_session):
    class FakeUserData:
        first_name = "Short"
        last_name = "Schema"
        email = "short.schema@example.com"
        username = "shortschema"
        password = "short"

    with pytest.raises(ValueError, match="Password must be at least 8 characters long"):
        User.register(db_session, FakeUserData())