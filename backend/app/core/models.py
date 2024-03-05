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
    input_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Created by User")
    )
    updated_at = models.DateTimeField(
        _("DTTOT Updated at"), auto_now=True)
    document_id = models.CharField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        max_length=36
    )
    dttot_id = models.TextField(
        default=uuid.uuid4,
        editable=False
    )
    _dttot_first_name = models.TextField(
        _("DTTOT First Name"),
        blank=True)
    _dttot_last_name = models.TextField(
        _("DTTOT Last Name"),
        blank=True)
    dttot_type = models.CharField(
        _("DTTOT Type"),
        max_length=50)
    _dttot_domicile_address1 = models.TextField(
        _("DTTOT Domicile Address"),
        blank=True)
    dttot_domicile_rt = models.IntegerField(
        _("DTTOT Domicile RT"),
        null=True,
        blank=True)
    dttot_domicile_rw = models.IntegerField(
        _("DTTOT Domicile RW"),
        null=True,
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
        null=True,
        blank=True)
    dttot_domicile_country = models.CharField(
        _("DTTOT Domicile Country"),
        max_length=50,
        blank=True)
    _dttot_description_1 = models.TextField(
        _("DTTOT Description 1"),
        blank=True)
    _dttot_description_2 = models.TextField(
        _("DTTOT Description 2"),
        blank=True)
    _dttot_description_3 = models.TextField(
        _("DTTOT Description 2"),
        blank=True)
    dttot_description_4 = models.TextField(
        _("DTTOT Description 2"),
        blank=True)
    dttot_description_5 = models.TextField(
        _("DTTOT Description 2"),
        blank=True)
    _dttot_nik_ktp = models.TextField(
        _("DTTOT NIK KTP"),
        blank=True)
    _dttot_passport_number = models.TextField(
        _("DTTOT Passport Number"),
        blank=True)
    dtott_job = models.TextField(
        _("DTTOT Job"),
        blank=True)
    _dttot_work_number = models.TextField(
        _("DTTOT Work Number"),
        blank=True)
    _dttot_mobile_number = models.TextField(
        _("DTTOT Mobile Number"),
        blank=True)
    _dttot_home_number = models.TextField(
        _("DTOTT Home Number"),
        blank=True)
    _dttot_socialmedia_instagram = models.TextField(
        _("DTTOT Instagram Accoun"),
        blank=True)
    _dttot_socialmedia_facebook = models.TextField(
        _("DTTOT Facebook Account"),
        blank=True)
    _dttot_socialmedia_x = models.TextField(
        _("DTTOT X account"),
        blank=True)
    _dttot_organization_name = models.TextField(
        _("DTTOT Organization Name"),
        blank=True)
    _dttot_kartukeluarga_number = models.TextField(
        _("DTTOT Nomor Kartu Keluarga"),
        blank=True)
    dttot_domicile_city = models.CharField(
        _("DTTOT Domicile City outside Indonesia"),
        max_length=50,
        blank=True)
    dttot_domicile_district = models.CharField(
        _("DTTOT Domicile District outside Indonesia"),
        max_length=50,
        blank=True)
    dttot_domicile_subdistrict = models.CharField(
        _("DTTOT Domicile Subdistrict outside Indonesia"),
        max_length=50,
        blank=True)
    _dttot_kode_densus = models.TextField(
        _("DTTOT Densus Code"),
        blank=True)
    dttot_birth_place_type = models.CharField(
        _("DTTOT Type of Birth Place that we know (City, Country, etc)"),
        max_length=50,
        blank=True)
    _dttot_birth_place = models.TextField(
        _("DTTOT Birth Place"),
        blank=True)
    _dttot_organization_created_by = models.TextField(
        _("DTTOT PIC / Founder of Organization"),
        blank=True)

    # Encrypt sensitive fields before saving
    def save(self, *args, **kwargs):
        self._dttot_first_name = fernet.encrypt(
            self._dttot_first_name.encode()
        ).decode() if self._dttot_first_name else ''
        self._dttot_last_name = fernet.encrypt(
            self._dttot_last_name.encode()
        ).decode() if self._dttot_last_name else ''
        self._dttot_domicile_address1 = fernet.encrypt(
            self._dttot_domicile_address1.encode()
        ).decode() if self._dttot_domicile_address1 else ''
        self._dttot_kartukeluarga_number = fernet.encrypt(
            self._dttot_kartukeluarga_number.encode()
        ).decode() if self._dttot_kartukeluarga_number else ''
        self._dttot_kode_densus = fernet.encrypt(
            self._dttot_kode_densus.encode()
        ).decode() if self._dttot_kode_densus else ''
        self._dttot_description_1 = fernet.encrypt(
            self._dttot_description_1.encode()
        ).decode() if self._dttot_description_1 else ''
        self._dttot_description_2 = fernet.encrypt(
            self._dttot_description_2.encode()
        ).decode() if self._dttot_description_2 else ''
        self._dttot_description_3 = fernet.encrypt(
            self._dttot_description_3.encode()
        ).decode() if self._dttot_description_3 else ''
        self._dttot_passport_number = fernet.encrypt(
            self._dttot_passport_number.encode()
        ).decode() if self._dttot_passport_number else ''
        self._dttot_nik_ktp = fernet.encrypt(
            self._dttot_nik_ktp.encode()
        ).decode() if self._dttot_nik_ktp else ''
        self._dttot_work_number = fernet.encrypt(
            self._dttot_work_number.encode()
        ).decode() if self._dttot_work_number else ''
        self._dttot_mobile_number = fernet.encrypt(
            self._dttot_mobile_number.encode()
        ).decode() if self._dttot_mobile_number else ''
        self._dttot_home_number = fernet.encrypt(
            self._dttot_home_number.encode()
        ).decode() if self._dttot_home_number else ''
        self._dttot_socialmedia_instagram = fernet.encrypt(
            self._dttot_socialmedia_instagram.encode()
        ).decode() if self._dttot_socialmedia_instagram else ''
        self._dttot_socialmedia_facebook = fernet.encrypt(
            self._dttot_socialmedia_facebook.encode()
        ).decode() if self._dttot_socialmedia_facebook else ''
        self._dttot_socialmedia_x = fernet.encrypt(
            self._dttot_socialmedia_x.encode()
        ).decode() if self._dttot_socialmedia_x else ''
        self._dttot_organization_name = fernet.encrypt(
            self._dttot_organization_name.encode()
        ).decode() if self._dttot_organization_name else ''

        super().save(*args, **kwargs)

    # Decrypt data when accessed
    @property
    def dttot_first_name(self):
        return fernet.decrypt(
            self._dttot_first_name.encode()
        ).decode() if self._dttot_first_name else ''

    @property
    def dttot_last_name(self):
        return fernet.decrypt(
            self._dttot_last_name.encode()
        ).decode() if self._dttot_last_name else ''

    @property
    def dttot_description_1(self):
        return fernet.decrypt(
            self._dttot_description_1.encode()
        ).decode() if self._dttot_description_1 else ''

    @property
    def dttot_description_2(self):
        return fernet.decrypt(
            self._dttot_description_2.encode()
        ).decode() if self._dttot_description_2 else ''

    @property
    def dttot_description_3(self):
        return fernet.decrypt(
            self._dttot_description_3.encode()
        ).decode() if self._dttot_description_3 else ''

    @property
    def dttot_passport_number(self):
        return fernet.decrypt(
            self._dttot_passport_number.encode()
        ).decode() if self._dttot_passport_number else ''

    @property
    def dttot_nik_ktp(self):
        return fernet.decrypt(
            self._dttot_nik_ktp.encode()
        ).decode() if self._dttot_nik_ktp else ''

    @property
    def dttot_work_number(self):
        return fernet.decrypt(
            self._dttot_work_number.encode()
        ).decode() if self._dttot_work_number else ''

    @property
    def dttot_mobile_number(self):
        return fernet.decrypt(
            self._dttot_mobile_number.encode()
        ).decode() if self._dttot_mobile_number else ''

    @property
    def dttot_home_number(self):
        return fernet.decrypt(
            self._dttot_home_number.encode()
        ).decode() if self._dttot_home_number else ''

    @property
    def dttot_socialmedia_instagram(self):
        return fernet.decrypt(
            self._dttot_socialmedia_instagram.encode()
        ).decode() if self._dttot_socialmedia_instagram else ''

    @property
    def dttot_socialmedia_facebook(self):
        return fernet.decrypt(
            self._dttot_socialmedia_facebook.encode()
        ).decode() if self._dttot_socialmedia_facebook else ''

    @property
    def dttot_socialmedia_x(self):
        return fernet.decrypt(
            self._dttot_socialmedia_x.encode()
        ).decode() if self._dttot_socialmedia_x else ''

    @property
    def dttot_organization_name(self):
        return fernet.decrypt(
            self._dttot_organization_name.encode()
        ).decode() if self._dttot_organization_name else ''

    def __str__(self):
        return f"{self.dttot_first_name} {self.dttot_last_name} - {self.dttot_type}"  # noqa
