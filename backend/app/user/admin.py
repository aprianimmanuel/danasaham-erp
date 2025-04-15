"""Django admin customization."""

from __future__ import annotations

from typing import ClassVar

import pytz  #type: ignore  # noqa: PGH003
from django.contrib import admin  #type: ignore  # noqa: PGH003
from django.contrib.auth.admin import (  #type: ignore # noqa: PGH003
    UserAdmin as BaseUserAdmin,  #type: ignore  # noqa: PGH003
)
from django.utils import timezone  #type: ignore  # noqa: PGH003
from django.utils.translation import gettext as _  #type: ignore  # noqa: PGH003

from app.user.models import Profile, User  #type: ignore  # noqa: PGH003


class UserProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "User Profile"
    fk_name = "user"

class UserAdmin(BaseUserAdmin):
    filter_horizontal = ("groups", "user_permissions")
    inlines = (UserProfileInline,)
    ordering: ClassVar[list[str]] = ["user_id"]
    list_display: ClassVar[list[str]] = [
        "email",
        "username",
        "get_first_name",
        "get_last_name",
        "is_active",
        "is_staff",
        "is_superuser",
        "custom_last_login",
    ]
    list_filter: ClassVar[list[str]] = ["is_active", "is_staff", "is_superuser"]
    search_fields: ClassVar[list[str]] = [
        "email",
        "username",
        "profile__first_name",
        "profile__last_name",
    ]
    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        (_("Permissions"), {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
        }),
        (_("Important dates"), {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2"),
        }),
    )
    readonly_fields: ClassVar[list[str]] = ["last_login"]

    def get_first_name(self, obj: User) -> str:
        """Return first name from profile, or '-' if profile doesn't exist."""
        return getattr(obj.profile, "first_name", "-")

    get_first_name.short_description = "First Name" # type: ignore  # noqa: PGH003

    def get_last_name(self, obj: User) -> str:
        """Return last name from profile, or '-' if profile doesn't exist."""
        return getattr(obj.profile, "last_name", "-")

    get_last_name.short_description = "Last Name" # type: ignore  # noqa: PGH003

    def custom_last_login(self, obj: User) -> str:
        """Display last login time in GMT+7 timezone."""
        if obj.last_login:
            local_time = timezone.localtime(obj.last_login, pytz.timezone("Asia/Jakarta"))
            return local_time.strftime("%Y-%m-%d %H:%M:%S")
        return _("Never logged in")

    custom_last_login.short_description = _("Last Login (GMT+7)") # type: ignore  # noqa: PGH003

admin.site.register(User, UserAdmin)
