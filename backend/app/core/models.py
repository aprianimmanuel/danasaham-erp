"""
Database models.
"""

from django.db import models
from django.contrib.auth.models import (
  AbstractBaseUser,
  BaseUserManager,
  PermissionsMixin
)
from django.utils.translation import gettext_lazy as _
from django_otp.util import random_hex
from django_otp.oath import totp
import secrets
import string


class UserManager(BaseUserManager):
    """Create, save and return a new user."""
    def create_user(self,
                    email,
                    username,
                    password=None,
                    **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))

        user = self.model(email=self.normalize_email(email), username=username, **extra_fields)  # noqa
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self,
                         email,
                         username, password=None,
                         **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, username, password, **extra_fields)

    @staticmethod
    def create_verification_code():
        """Generate a random verification code."""
        return ''.join(secrets.choice(string.digits) for _ in range(6))


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(_('email_address'), unique=True)
    username = models.CharField(_('username'), max_length=150, unique=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    totp_secret_key = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        help_text=_('A hex-encoded 20-byte secret key'))

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    def generate_totp_secret(self):
        """Generate a TOTP secret key for the user."""
        self.totp_secret_key = random_hex(20)
        self.save()

    def verify_totp_token(self, token, tolerance=1):
        """Verify a TOTP token provided by the user."""
        if not self.totp_secret_key:
            return False
        key = bytes.fromhex(self.totp_secret_key)
        verified = totp(key) == int(token)
        return verified
