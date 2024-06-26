"""Django admin customization."""

from __future__ import annotations

import pytz
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext as _

from .models import Document, User, UserProfile, dttotDoc


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "UserProfile"
    fk_name = "user"


class UserAdmin(BaseUserAdmin):
    filter_horizontal = ("groups", "user_permissions")
    inlines = (UserProfileInline,)
    ordering = ["user_id"]
    list_display = [
        "email",
        "username",
        "get_first_name",
        "get_last_name",
        "is_active",
        "is_staff",
        "is_superuser",
        "custom_last_login",
    ]
    list_filter = ["is_active", "is_staff", "is_superuser"]
    search_fields = ["email", "username", "profile__first_name", "profile__last_name"]
    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        (_("Personal Info"), {"fields": ()}),  # Removed 'username' to avoid duplication
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2"),
            },
        ),
    )
    readonly_fields = ["last_login"]

    def get_first_name(self, obj):
        return obj.profile.first_name if hasattr(obj, "profile") else "-"

    get_first_name.short_description = "First Name"

    def get_last_name(self, obj):
        return obj.profile.last_name if hasattr(obj, "profile") else "-"

    get_last_name.short_description = "Last Name"

    def custom_last_login(self, obj):
        """Custom representation of last_login field to display time in GMT+7."""
        if obj.last_login:
            last_login_gmt7 = obj.last_login + timezone.timedelta(hours=7)
            return last_login_gmt7.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return _("Never logged in")

    custom_last_login.short_description = _("Last Login (GMT+7)")


class DttotDocAdmin(admin.ModelAdmin):
    list_display = [
        "document_id",
        "dttot_id",
        "dttot_type",
        "display_username",
        "formatted_updated_at",
    ]
    search_fields = [
        "dttot_id",
        "dttot_type",
        "dttot_first_name",
        "dttot_last_name",
        "user__username",
    ]
    list_filter = ["dttot_type", "updated_at"]
    readonly_fields = ("document_id", "dttot_id")

    def display_username(self, obj):
        return obj.user.username

    display_username.short_description = "username"

    def formatted_updated_at(self, obj):
        local_tz = pytz.timezone("Asia/Jakarta")  # GMT+7 timezone
        local_time = timezone.localtime(obj.updated_at, local_tz)
        return format_html(
            "<span>{} (GMT+7)</span>",
            local_time.strftime("%Y-%m-%d %H:%M:%S"),
        )

    formatted_updated_at.short_description = "Updated At (GMT+7)"


class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        "document_id",
        "document_name",
        "document_type",
        "created_by_username",
        "updated_by_username",
    ]
    search_fields = (
        "document_name",
        "document_type",
        "created_by__username",
        "updated_by__username",
    )
    readonly_fields = ("document_id",)

    def created_by_username(self, obj):
        return obj.created_by.username

    created_by_username.short_description = "username"

    def updated_by_username(self, obj):
        return obj.updated_by.username

    updated_by_username.short_description = "username"


admin.site.register(dttotDoc, DttotDocAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(User, UserAdmin)
