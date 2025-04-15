from __future__ import annotations

import uuid
from typing import Any

from django.conf import settings  #type: ignore  # noqa: PGH003
from django.contrib.auth.hashers import make_password  #type: ignore  # noqa: PGH003
from django.contrib.auth.models import (  #type: ignore  # noqa: PGH003
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models  #type: ignore  # noqa: PGH003
from django.utils.translation import gettext_lazy as _  #type: ignore  # noqa: PGH003


class UserManager(BaseUserManager):
    """Manager for user profiles."""

    def create_user(
        self, email: str, username: str, password: str | None = None, **extra_fields: Any,
    ) -> User:
        """Create and return a new user.

        Args:
        ----
            email (str): The email address of the user.
            username (str): The username of the user.
            password (Optional[str], optional): The password for the user. Defaults to None.
            **extra_fields (Any): Additional fields to be set on the user.

        Raises:
        ------
            ValueError: If no email is provided.

        Returns:
        -------
            User: The newly created user.

        """
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, username: str, password: str | None = None, **extra_fields: Any,
    ) -> User:
        """Create and return a new superuser.

        Args:
        ----
            email (str): The email address of the user.
            username (str): The username of the user.
            password (Optional[str], optional): The password for the user. Defaults to None.
            **extra_fields (Any): Additional fields to be set on the user.

        Returns:
        -------
            User: The newly created user.

        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""

    user_id = models.CharField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        max_length=36,
        verbose_name=_("User ID"),
        unique=True,
    )
    created_date = models.DateTimeField(_("created_date"), auto_now_add=True)
    updated_date = models.DateTimeField(_("updated_date"), auto_now=True)
    email = models.EmailField(_("email_address"), unique=True)
    password = models.CharField(_("password"), max_length=128)
    username = models.CharField(_("username"), max_length=150, unique=True)
    is_active = models.BooleanField(_("active"), default=True)
    is_staff = models.BooleanField(_("staff status"), default=False)
    email_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # noqa: RUF012

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self) -> str:
        return self.email

    def save(
        self, *args: Any, **kwargs: Any,
    ) -> None:
        """Ensure password is hashed before saving.

        Args:
        ----
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
        -------
            None

        """
        if self.password and not self.password.startswith("pbkdf2_sha256"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)


class Profile(models.Model):
    profile_id = models.CharField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        max_length=36,
        verbose_name=_("Profile ID"),
        unique=True,
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    created_date = models.DateTimeField(auto_now=True)
    updated_date = models.DateTimeField(auto_now_add=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    first_name = models.CharField(_("First Name"), max_length=50, blank=True)
    last_name = models.CharField(_("Last Name"), max_length=50, blank=True)

    def __str__(self) -> str:
        return self.user.first_name

class EmailVerificationCode(models.Model):
    verificationcode_id = models.CharField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        max_length=36,
        unique=True,
    )
    user = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="verificationcode",
        related_query_name="verificationcode",
    )
    type_used = models.CharField(max_length=255, blank=True)
    status_used = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now=True)
    updated_date = models.DateTimeField(auto_now_add=False, null=True)
    verification_code = models.CharField(max_length=8, blank=True)

    def __str__(self) -> str:
        return self.user.verification_code
