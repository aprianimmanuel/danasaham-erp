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
from cryptography.fernet import Fernet
import uuid
import os
from dotenv import load_dotenv
from django.conf import settings


# Load environment variables
load_dotenv()

# Retrieve the FERNET_KEY from your environment variables
FERNET_KEY = os.getenv('FERNET_KEY')
if not FERNET_KEY:
    raise ValueError(
        "No FERNET_KEY found in environment variables. Make sure to set it in your .env file")  # noqa

fernet = Fernet(FERNET_KEY.encode())


class UserManager(BaseUserManager):
    """Manager for user profiles."""
    def create_user(self, email, username, password=None, **extra_fields):
        """Create and return a new user."""
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """Create and return a new superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    user_id = models.CharField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        max_length=36)
    email = models.EmailField(_('email_address'), unique=True)
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        null=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    otp_attempts = models.IntegerField(default=0)
    last_otp_time = models.DateTimeField(null=True, blank=True)
    totp_secret_key = models.TextField(
        null=True,
        blank=True,
        editable=False
    )
    email_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    # Encrypt the totp_secret_key before saving
    def save(self, *args, **kwargs):
        if self.totp_secret_key:
            self.totp_secret_key = fernet.encrypt(
                self.totp_secret_key.encode()).decode()
        super(User, self).save(*args, **kwargs)

    # Method to decrypt totp_secret_key when accessed
    def get_totp_secret_key(self):
        if self.totp_secret_key:
            return fernet.decrypt(self.totp_secret_key.encode()).decode()
        return None


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile')
    bio = models.TextField(
        max_length=500, blank=True
    )
    phone_number = models.CharField(
        max_length=30, blank=True
    )
    birth_date = models.DateField(
        null=True,
        blank=True
    )
    first_name = models.CharField(_("First Name"), max_length=50, blank=True)
    last_name = models.CharField(_("Last Name"), max_length=50, blank=True)

    def __str__(self):
        return self.user.username


class dttotDoc(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Created by User")
    )
    created_at = models.DateTimeField(
        _("DTTOT Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(
        _("DTTOT Updated at"), auto_now=True)
    document_id = models.CharField(
        default=uuid.uuid4,
        editable=False,
        max_length=36
    )
    dttot_id = models.CharField(
        default=uuid.uuid4,
        editable=False,
        max_length=20)
    dttot_first_name = models.CharField(
        _("DTTOT First Name"),
        max_length=50,
        blank=True)
    dttot_last_name = models.CharField(
        _("DTTOT Last Name"),
        max_length=50,
        blank=True)
    dttot_type = models.CharField(_("DTTOT Type"), max_length=50)
    dttot_domicile_address1 = models.TextField(
        _("DTTOT Domicile Address"),
        blank=True)
    dttot_domicile_rt = models.IntegerField(
        _("DTTOT Domicile RT"),
        blank=True)
    dttot_domicile_rw = models.IntegerField(
        _("DTTOT Domicile RW"),
        blank=True)
    dttot_domicile_kelurahan = models.CharField(
        _("DTTOT Domicile Kelurahan"),
        max_length=50,
        blank=True)
    dttot_domicile_kecamatan = models.CharField(
        _("DTTOT Domicile Kecamatan"),
        max_length=50,
        blank=True)
    dttot_domicile_kabupaten = models.CharField(
        _("DTTOT Domicile Kabupaten"),
        max_length=50,
        blank=True)
    dttot_domicile_kota = models.CharField(
        _("DTTOT Domicile Kota"),
        max_length=50,
        blank=True)
    dttot_domicile_provinsi = models.CharField(
        _("DTTOT Domicile Provinsi"),
        max_length=50,
        blank=True)
    dttot_domicile_postal_code = models.IntegerField(
        _("DTTOT Domicile Postal code"),
        blank=True)

    def __str__(self):
        return f"{self.dttot_first_name} {self.dttot_last_name} - {self.dttot_type}"  # noqa
