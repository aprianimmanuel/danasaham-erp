"""
Django admin customization
"""

from django.contrib import admin
from django.utils.translation import gettext as _
from .models import dttotDoc, Document


class DttotDocAdmin(admin.ModelAdmin):
    list_display = [
        'document_id',
        'dttot_id',
        'dttot_type',
        'display_username',
        'updated_at'
    ]
    search_fields = [
        'dttot_id',
        'dttot_type',
        'dttot_first_name',
        'dttot_last_name',
        'user__username'
    ]
    list_filter = [
        'dttot_type',
        'updated_at'
    ]
    readonly_fields = ('document_id', 'dttot_id')

    def display_username(self, obj):
        return obj.user.username
    display_username.short_description = 'username'


class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        'document_id',
        'document_name',
        'document_type',
        'created_by_username',
        'updated_by_username',
    ]
    search_fields = (
        'document_name',
        'document_type',
        'created_by__username',
        'updated_by__username',
    )
    readonly_fields = ('document_id',)

    def created_by_username(self, obj):
        return obj.created_by.username
    created_by_username.short_description = 'username'

    def updated_by_username(self, obj):
        return obj.updated_by.username
    updated_by_username.short_description = 'username'


admin.site.register(dttotDoc, DttotDocAdmin)
admin.site.register(Document, DocumentAdmin)
