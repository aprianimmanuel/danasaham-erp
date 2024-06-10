from __future__ import annotations

from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from app.user.models import User, UserProfile
from django.utils.translation import gettext as _


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'UserProfile'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    filter_horizontal = ("groups", "user_permissions")
    inlines = (UserProfileInline, )
    ordering = ['user_id']
    list_display = [
        'email',
        'username',
        'get_first_name',
        'get_last_name',
        'is_active',
        'is_staff',
        'is_superuser',
        'custom_last_login',]
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    search_fields = [
        'email', 'username', 'profile__first_name', 'profile__last_name']
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Personal Info'), {'fields': ('username',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    readonly_fields = ['last_login']

    def get_first_name(self, obj):
        return obj.profile.first_name if hasattr(obj, 'profile') else '-'
    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.profile.last_name if hasattr(obj, 'profile') else '-'
    get_last_name.short_description = 'Last Name'

    def custom_last_login(self, obj):
        """
        Custom representation of last_login field to display time in GMT+7
        """

        if obj.last_login:
            last_login_gmt7 = obj.last_login + timezone.timedelta(hours=7)
            return last_login_gmt7.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return _('Never logged in')

    custom_last_login.short_description = _('Last Login (GMT+7)')

    def save_model(
        self,
        request: Any,
        obj: User,
        form: None,
        change: bool,  # noqa: FBT001
    ) -> None:
        """Update user password if it is not raw.

        This is needed to hash password when updating user from admin panel.
        """
        has_raw_password = obj.password.startswith("pbkdf2_sha256")
        if not has_raw_password:
            obj.set_password(obj.password)

        super().save_model(request, obj, form, change)


admin.site.register(User, UserAdmin)