"""
Database models.
"""
import uuid
from django.db import models
from django.contrib.auth.models import (
  AbstractBaseUser,
  BaseUserManager,
  PermissionsMixin
)
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils.timezone import now


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
    email_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email


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
    last_name = models.CharField(
        _("Last Name"),
        max_length=50,
        blank=True,
        null=True)

    def __str__(self):
        return self.user.username


def document_directory_path(instance, filename):
    date_now = instance.created_date or now()
    return 'documents/{document_type}/{year}/{month}/{day}/{created_by}/{filename}'.format(  # noqa
        document_type=instance.document_type,
        year=date_now.year,
        month=date_now.strftime('%m'),
        day=date_now.strftime('%d'),
        created_by=instance.created_by.user_id if instance.created_by else 'unknown',  # noqa
        filename=filename
    )


class Document(models.Model):
    document_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    document_file = models.FileField(
        upload_to=document_directory_path,
        blank=True,
        null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    document_id = models.CharField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        max_length=36,
    )
    document_file_type = models.CharField(
        _(
            "Document File Type (PDF, XLS, TEXT, or etc)"),
        max_length=50,
        null=True,
        blank=True)
    document_type = models.CharField(
        _("Document Type"), max_length=50)
    updated_date = models.DateTimeField(
        _("Date when Document modified"), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_documents")
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="updated_documents")

    def __str__(self):
        return self.document_name


class dttotDoc(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_("Created by User"),
        null=True
    )
    updated_at = models.DateTimeField(
        _("DTTOT Updated at"), auto_now=True)

    document = models.ForeignKey(
        'Document',
        on_delete=models.SET_NULL,
        related_name='dttotDocs',
        related_query_name='dttotDoc',
        null=True
    )
    dttot_id = models.TextField(
        default=uuid.uuid4,
        primary_key=True,
        max_length=36,
        editable=False
    )
    dttot_first_name = models.TextField(
        _("DTTOT First Name"),
        blank=True)
    dttot_middle_name = models.TextField(
        _("DTTOT Middle Name"),
        blank=True,
        null=True)
    dttot_last_name = models.TextField(
        _("DTTOT Last Name"),
        blank=True,
        null=True)
    dttot_alias_name_1 = models.TextField(
        _("DTTOT Alias Name 1"),
        blank=True,
        null=True
    )
    dttot_alias_first_name_1 = models.TextField(
        _("DTTOT Alias First Name 1"),
        blank=True,
        null=True
    )
    dttot_alias_middle_name_1 = models.TextField(
        _("DTTOT Alias Middle Name 1"),
        blank=True,
        null=True)
    dttot_alias_last_name_1 = models.TextField(
        _("DTTOT Alias Last Name 1"),
        blank=True,
        null=True)
    dttot_alias_name_2 = models.TextField(
        _("DTTOT Alias Name 2"),
        blank=True,
        null=True
    )
    dttot_alias_first_name_2 = models.TextField(
        _("DTTOT Alias First Name 2"),
        blank=True,
        null=True
    )
    dttot_alias_middle_name_2 = models.TextField(
        _("DTTOT Alias Middle Name 2"),
        blank=True,
        null=True)
    dttot_alias_last_name_2 = models.TextField(
        _("DTTOT Alias Last Name 2"),
        blank=True,
        null=True)
    dttot_alias_name_3 = models.TextField(
        _("DTTOT Alias Name 3"),
        blank=True,
        null=True
    )
    dttot_alias_first_name_3 = models.TextField(
        _("DTTOT Alias First Name 3"),
        blank=True,
        null=True
    )
    dttot_alias_middle_name_3 = models.TextField(
        _("DTTOT Alias Middle Name 3"),
        blank=True,
        null=True
    )
    dttot_alias_last_name_3 = models.TextField(
        _("DTTOT Alias Last Name 3"),
        blank=True,
        null=True
    )
    dttot_alias_name_4 = models.TextField(
        _("DTTOT Alias Name 4"),
        blank=True,
        null=True
    )
    dttot_alias_first_name_4 = models.TextField(
        _("DTTOT Alias First Name 4"),
        blank=True,
        null=True
    )
    dttot_alias_middle_name_4 = models.TextField(
        _("DTTOT Alias Middle Name 4"),
        blank=True,
        null=True)
    dttot_alias_last_name_4 = models.TextField(
        _("DTTOT Alias Last Name 4"),
        blank=True,
        null=True)
    dttot_alias_name_5 = models.TextField(
        _("DTTOT Alias Name 5"),
        blank=True,
        null=True
    )
    dttot_alias_first_name_5 = models.TextField(
        _("DTTOT Alias First Name 5"),
        blank=True,
        null=True
    )
    dttot_alias_middle_name_5 = models.TextField(
        _("DTTOT Alias Middle Name 5"),
        blank=True,
        null=True)
    dttot_alias_last_name_5 = models.TextField(
        _("DTTOT Alias Last Name 5"),
        blank=True,
        null=True)
    dttot_type = models.TextField(
        _("DTTOT Type"),
        blank=True,
        null=True)
    dttot_kode_densus = models.TextField(
        _("DTTOT Kode Densus"),
        blank=True,
        null=True
    )
    dttot_birth_place = models.TextField(
        _("DTTOT Birth Place"),
        blank=True,
        null=True
    )
    dttot_birth_date_1 = models.TextField(
        _("DTTOT Birth Date 1"),
        blank=True,
        null=True)
    dttot_birth_date_2 = models.TextField(
        _("DTTOT Birth Date 2"),
        blank=True,
        null=True)
    dttot_birth_date_3 = models.TextField(
        _("DTTOT Birth Date 3"),
        max_length=255,
        blank=True,
        null=True)
    dttot_nationality_1 = models.TextField(
        _("DTTOT Nationality 1"),
        max_length=255,
        blank=True,
        null=True)
    dttot_nationality_2 = models.CharField(
        _("DTTOT Nationality 2"),
        max_length=255,
        blank=True,
        null=True)
    dttot_domicile_address = models.TextField(
        _("DTTOT Domicile Address"),
        max_length=4000,
        blank=True,
        null=True
    )
    dttot_description_1 = models.TextField(
        _("DTTOT Description 1"),
        max_length=4000,
        blank=True,
        null=True)
    dttot_description_2 = models.TextField(
        _("DTTOT Description 2"),
        max_length=4000,
        blank=True,
        null=True)
    dttot_description_3 = models.TextField(
        _("DTTOT Description 3"),
        max_length=4000,
        blank=True,
        null=True)
    dttot_description_4 = models.TextField(
        _("DTTOT Description 4"),
        max_length=4000,
        blank=True,
        null=True)
    dttot_description_5 = models.TextField(
        _("DTTOT Description 5"),
        max_length=4000,
        blank=True,
        null=True)
    dttot_nik_ktp = models.TextField(
        _("DTTOT NIK KTP"),
        blank=True,
        null=True)
    dttot_passport_number = models.TextField(
        _("DTTOT Passport Number"),
        blank=True,
        null=True)

    def __str__(self):
        return f"{self.dttot_first_name} {self.dttot_last_name} - {self.dttot_type}"  # noqa
