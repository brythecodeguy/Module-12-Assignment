import pytest
from uuid import uuid4
from datetime import datetime
from pydantic import ValidationError
from app.schemas.user import UserBase, PasswordMixin, UserCreate, UserLogin, UserResponse, PasswordUpdate
from app.schemas.base import BaseSchema


def test_user_base_valid():
    user = UserBase(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        username="johndoe"
    )
    assert user.email == "john@example.com"


def test_user_base_invalid_email():
    with pytest.raises(ValidationError):
        UserBase(
            first_name="John",
            last_name="Doe",
            email="bademail",
            username="johndoe"
        )


def test_password_valid():
    p = PasswordMixin(password="GoodPass123!")
    assert p.password == "GoodPass123!"


def test_password_too_short():
    with pytest.raises(ValidationError):
        PasswordMixin(password="short")


def test_password_missing_uppercase():
    with pytest.raises(ValidationError):
        PasswordMixin(password="lowercase123!")


def test_password_missing_lowercase():
    with pytest.raises(ValidationError):
        PasswordMixin(password="UPPERCASE123!")


def test_password_missing_digit():
    with pytest.raises(ValidationError):
        PasswordMixin(password="NoDigitsHere!")


def test_user_create_valid():
    user = UserCreate(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        username="johndoe",
        password="GoodPass123!",
        confirm_password="GoodPass123!"
    )
    assert user.username == "johndoe"


def test_user_create_invalid_password():
    with pytest.raises(ValidationError):
        UserCreate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            username="johndoe",
            password="short",
            confirm_password="short"
        )


def test_user_login_valid():
    user = UserLogin(username="johndoe", password="GoodPass123!")
    assert user.username == "johndoe"


def test_user_login_invalid():
    with pytest.raises(ValidationError):
        UserLogin(username="jd", password="short")


def test_password_missing():
    with pytest.raises(ValidationError):
        PasswordMixin()

def test_base_schema_from_attributes_enabled():
    schema = BaseSchema()
    assert schema.model_config["from_attributes"] is True

from app.schemas.user import UserResponse


def test_user_create_passwords_do_not_match():
    with pytest.raises(ValidationError):
        UserCreate(
            first_name="John",
            last_name="Doe",
            email="john2@example.com",
            username="johndoe2",
            password="GoodPass123!",
            confirm_password="DifferentPass123!"
        )


def test_password_missing_special_character():
    with pytest.raises(ValidationError):
        PasswordMixin(password="GoodPass123")


def test_user_response_from_attributes():
    class DummyUser:
        def __init__(self):
            self.id = uuid4()
            self.first_name = "John"
            self.last_name = "Doe"
            self.email = "john@example.com"
            self.username = "johndoe"
            self.is_active = True
            self.is_verified = False
            self.created_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()

    user = DummyUser()
    result = UserResponse.model_validate(user)

    assert result.username == "johndoe"
    assert result.email == "john@example.com"

def test_password_update_passwords_do_not_match():
    with pytest.raises(ValidationError, match="New password and confirmation do not match"):
        PasswordUpdate(
            current_password="OldPass123!",
            new_password="NewPass123!",
            confirm_new_password="Different123!"
        )


def test_password_update_new_password_must_differ():
    with pytest.raises(ValidationError, match="New password must be different from current password"):
        PasswordUpdate(
            current_password="SamePass123!",
            new_password="SamePass123!",
            confirm_new_password="SamePass123!"
        )

def test_password_update_valid():
    update = PasswordUpdate(
        current_password="OldPass123!",
        new_password="NewPass123!",
        confirm_new_password="NewPass123!"
    )

    assert update.current_password == "OldPass123!"
    assert update.new_password == "NewPass123!"
    assert update.confirm_new_password == "NewPass123!"