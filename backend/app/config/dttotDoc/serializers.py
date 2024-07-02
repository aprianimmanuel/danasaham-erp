from __future__ import annotations

from typing import Any, ClassVar

from rest_framework import serializers

from app.config.core.models import Document, User, dttotDoc, dttotDocReport
from app.config.documents.serializers import DocumentSerializer


class DttotDocSerializer(serializers.ModelSerializer):
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
        model = dttotDoc
        fields = "__all__"
        read_only_fields: ClassVar = ["dttot_id", "updated_at"]

    def create(self, validated_data: dict[str, Any]) -> dttotDoc:
        user = self.context.get("request").user if self.context.get("request") else None
        validated_data["user"] = validated_data.get("user", user)
        document = validated_data.pop("document", None)
        return dttotDoc.objects.create(document=document, **validated_data)

    def to_representation(self, instance: dttotDoc) -> dict[str, Any]:
        representation = super().to_representation(instance)
        representation["user_id"] = instance.user.user_id if instance.user else None
        representation["document_id"] = (
            instance.document.document_id if instance.document else None
        )
        return representation


class DttotDocListSerializer(serializers.ModelSerializer):
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
        model = dttotDoc
        fields: ClassVar = [
            "document",
            "dttot_id",
            "document_data",
            "updated_at",
            "user",
        ]


class DttotDocReportSerializer(serializers.ModelSerializer):
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
        model = dttotDocReport
        fields = "__all__"
        read_only_fields: ClassVar = ["dttot_search_id"]

    def create(self, validated_data: dict[str, Any]) -> dttotDocReport:
        user = self.context.get("request").user if self.context.get("request") else None
        validated_data["user"] = validated_data.get("user", user)
        document = validated_data.pop("document", None)
        return dttotDocReport.objects.create(document=document, **validated_data)
