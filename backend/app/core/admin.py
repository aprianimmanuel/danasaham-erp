"""
Django admin customization
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
from .models import User
from django.utils import timezone


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'username', 'is_active', 'is_staff', 'is_superuser']  # noqa
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    search_fields = ['email', 'username']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('username',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        (_('Important dates'), {'fields': ('custom_last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    readonly_fields = ['custom_last_login']

    def custom_last_login(self, obj):
        """
        Custom representation of last_login field to display time in GMT+7
        """

        if obj.last_login:
            last_login_gmt7 = obj.last_login + timezone.timedelta(hours=7)
            return last_login_gmt7.strftime('%Y-%m-%d %H:%M:%S')
        else:
            return None

    custom_last_login.short_description = _('Last Login (GMT+7)')


admin.site.register(User, UserAdmin)
