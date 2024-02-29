"""
Django admin customization
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
from .models import User, UserProfile
from django.utils import timezone


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'UserProfile'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, )
    ordering = ['user_id']
    list_display = [
        'email',
        'username',
        'get_first_name',
        'get_last_name',
        'is_active',
        'is_staff',
        'is_superuser']
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    search_fields = [
        'email', 'username', 'profile__first_name', 'profile__last_name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('username',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
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


admin.site.register(User, UserAdmin)
