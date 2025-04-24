from __future__ import annotations

from datetime import date

import pytest
from django.contrib.auth import get_user_model  # type: ignore  # noqa: PGH003

from app.user.user_profile.models import UserProfile  # type: ignore  # noqa: PGH003


@pytest.mark.django_db
class TestUserProfileModel:
    def test_user_profile_model(
        self,
    ) -> None:
        """Test creating a `UserProfile` with a `User`.

        Args:
            self (TestUserProfileModel): The instance of this test class.

        Returns:
            None

        """
        # Arrange: Create dummy user
        user = get_user_model()
        user_objects = user.objects.create_user(
            username="johndoe",
            email="johndoe@me.com",
            password="Testp@ss123",  # noqa: S106
        )

        # Act: Create user profile
        profile: UserProfile = UserProfile.objects.create(
            user=user_objects,
            bio="This is a test bio.",
            phone_number="1234567890",
            birth_date=date(1990, 1, 1),
            first_name="John",
            last_name="Doe",
        )

        # Assert
        assert profile.profile_id is not None
        assert profile.user == user
        assert profile.bio == "This is a test bio."
        assert profile.phone_number == "1234567890"
        assert profile.birth_date == date(1990, 1, 1)
        assert profile.first_name == "John"
        assert profile.last_name == "Doe"

    def test_user_profile_str_returns_username(
        self,
    ) -> None:
        """Test that the `__str__` method returns the username.

        Args:
            self (TestUserProfileModel): The instance of this test class.

        Returns:
            None

        """
        # Arrange: Create dummy user
        user = get_user_model()
        user_objects = user.objects.create_user(
            username="johndoe",
            email="johndoe@me.com",
            password="Testp@ss123",  # noqa: S106
        )

        # Act: Create user profile
        profile: UserProfile = UserProfile.objects.create(
            user=user_objects,
            bio="This is a test bio.",
            phone_number="1234567890",
            birth_date=date(1990, 1, 1),
            first_name="John",
            last_name="Doe",
        )

        # Assert
        assert str(profile) == "johndoe"
