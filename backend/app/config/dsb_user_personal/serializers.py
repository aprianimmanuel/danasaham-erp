from __future__ import annotations

from rest_framework import serializers

from app.config.core.models import Document, User, dsb_user_personal
from app.config.documents.serializers import DocumentSerializer


class DsbUserPersonalSerializer(serializers.ModelSerializer):
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
        model = dsb_user_personal
        fields = "__all__"
        read_only_fields = [
            "dsb_user_personal_id",
            "created_date",
            "updated_date",
            "last_update_by",
            "initial_registration_date",
            "coredsb_user_id",
            "user_upgrade_to_personal_date",
            "users_last_modified_date",
            "personal_legal_last_modified_date",
        ]

    def create(self, validated_data):
        user = self.context.get("request").user if self.context.get("request") else None
        validated_data["user"] = validated_data.get("user", user)
        document = validated_data.pop("document", None)
        return dsb_user_personal.objects.create(document=document, **validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user_id"] = instance.user.user_id if instance.user else None
        representation["document_id"] = (
            instance.document.document_id if instance.document else None
        )
        return representation
