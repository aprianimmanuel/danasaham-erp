from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model  # type: ignore  # noqa: PGH003
from django.core.exceptions import ValidationError  # type: ignore  # noqa: PGH003

User = get_user_model()


@pytest.mark.django_db
def test_create_user_success() -> None:
    """Test creating a new user with an email is successful.

    Returns:
        None

    """
    user = User.objects.create_user(
        email="test@example",
        username="testuser",
        password="Testp@ss!23",  # noqa: S106
    )

    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_superuser is False
    assert user.is_email_verified is False
    assert user.password.startswith("pbkdf2_sha256$")

@pytest.mark.django_db
def test_create_user_without_email_raises_error() -> None:
    """Test creating a new user without an email raises an error.

    The `create_user` method should raise a `ValueError` if the
    `email` argument is empty.

    Parameters
    ----------
        None

    Returns
    -------
        None

    """
    with pytest.raises(ValueError) as exc_info:  # noqa: PT011
        User.objects.create_user(
            email="",
            username="noemail",
            password="nopassword",  # noqa: S106
        )

    assert "The Email field must be set." in str(exc_info.value)

@pytest.mark.django_db
def test_create_superuser_success(
    email: str = "admin@example.com",
    username: str = "adminuser",
    password: str = "adminpass123",  # noqa: S107
) -> User:  # type: ignore  # noqa: PGH003
    """Test creating a superuser with the given credentials.

    Args:
        email (str): The email address for the user.
        username (str): The username for the user.
        password (str): The password for the user.

    Returns:
        User: The newly created superuser.

    """
    superuser = User.objects.create_superuser(
        email=email,
        username=username,
        password=password,
    )

    assert superuser.email == "admin@example.com"
    assert superuser.username == "adminuser"
    assert superuser.is_active is True
    assert superuser.is_staff is True
    assert superuser.is_superuser is True

@pytest.mark.django_db
def test_user_str_returns_email() -> None:
    """Test that the __str__ method returns the email of the user.

    Returns:
        None

    """
    user = User.objects.create_user(
        email="test@example",
        username="hellouser",
        password="Testp@ss!23",  # noqa: S106
    )
    assert str(user) == "test@example"

@pytest.mark.django_db
def test_password_is_hashed_when_saving_manually(
    email: str = "test@example",
    username: str = "hellouser",
    password: str = "Testp@ss!23",  # noqa: S107
) -> None:
    """Test that the password is hashed when saving a user manually.

    Args:
        email (str): The email address for the user.
        username (str): The username for the user.
        password (str): The password for the user.

    Returns:
        None

    """
    user = User.objects.create_user(
        email=email,
        username=username,
        password=password,
    )
    user.save()

    assert user.password.startswith("pbkdf2_sha256$")
    assert user.password != "plaintext123"  # noqa: S105

@pytest.mark.django_db
def test_unique_username_constraint() -> None:
    """Test that creating a user with a duplicate username raises an IntegrityError.

    Returns:
        None

    """
    User.objects.create_user(
        email="test@example",
        username="hellouser",
        password="Testp@ss!23",  # noqa: S106
    )
    with pytest.raises(ValidationError):
        User.objects.create_user(
            email="test@example",
            username="hellouser",
            password="Testp@ss!23",  # noqa: S106
        )
