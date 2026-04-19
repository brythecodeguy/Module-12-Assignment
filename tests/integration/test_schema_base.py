import pytest
from pydantic import ValidationError
from app.schemas.user import UserBase, PasswordMixin, UserCreate, UserLogin


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
    p = PasswordMixin(password="GoodPass123")
    assert p.password == "GoodPass123"


def test_password_too_short():
    with pytest.raises(ValidationError):
        PasswordMixin(password="short")


def test_password_missing_uppercase():
    with pytest.raises(ValidationError):
        PasswordMixin(password="lowercase123")


def test_password_missing_lowercase():
    with pytest.raises(ValidationError):
        PasswordMixin(password="UPPERCASE123")


def test_password_missing_digit():
    with pytest.raises(ValidationError):
        PasswordMixin(password="NoDigitsHere")


def test_user_create_valid():
    user = UserCreate(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        username="johndoe",
        password="GoodPass123"
    )
    assert user.username == "johndoe"


def test_user_create_invalid_password():
    with pytest.raises(ValidationError):
        UserCreate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            username="johndoe",
            password="short"
        )


def test_user_login_valid():
    user = UserLogin(username="johndoe", password="GoodPass123")
    assert user.username == "johndoe"


def test_user_login_invalid():
    with pytest.raises(ValidationError):
        UserLogin(username="jd", password="short")
        
def test_password_missing():
    with pytest.raises(ValidationError):
        PasswordMixin()