from __future__ import annotations

from rest_framework import serializers

from app.config.core.models import Document, User, dsb_user_publisher
from app.config.documents.serializers import DocumentSerializer


class DsbUserPublisherSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
        required=False,
    )
    document = serializers.PrimaryKeyRelatedField(
        queryset=Document.objects.all(),
        required=True,
    )
    document_data = DocumentSerializer(read_only=True, source="document")

    class Meta:
        model = dsb_user_publisher
        fields = "__all__"
        read_only_fields = [
            "dsb_user_publisher_id",
            "created_date",
            "updated_date",
            "last_update_by",
            "initial_registration_date",
        ]
