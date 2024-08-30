from __future__ import annotations

import uuid
from typing import Any, ClassVar

from django.utils import timezone
from rest_framework import serializers

from app.config.core.models import Document, User, dttotDoc
from app.config.documents.serializers import DocumentSerializer


class DttotDocSerializer(serializers.ModelSerializer):
    last_update_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
        required=False,
        allow_null=True,
    )
    document = serializers.PrimaryKeyRelatedField(
        queryset=Document.objects.all(),
        required=True,
    )
    updated_at = serializers.DateTimeField(read_only=True)
    dttot_id = serializers.CharField(
        default=uuid.uuid4,
        read_only=True)
    document_data = DocumentSerializer(read_only=True, source="document")

    class Meta:
        model = dttotDoc
        fields = "__all__"
        read_only_fields: ClassVar = ["dttot_id", "updated_at"]

    def create(self, validated_data: dict[str, Any]) -> dttotDoc:
        document = validated_data.pop("document", None)
        return dttotDoc.objects.create(document=document, **validated_data)

    def update(self, instance: dttotDoc, validated_data: dict[str, Any]) -> dttotDoc:
        # Handle update logic
        user = self.context.get("request").user if self.context.get("request") else None
        instance.last_update_by = user
        instance.updated_at = timezone.now
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance: dttotDoc) -> dict[str, Any]:
        representation = super().to_representation(instance)
        representation["document_id"] = (
            instance.document.document_id if instance.document else None
        )
        return representation


class DttotDocListSerializer(serializers.ModelSerializer):
    last_update_by = serializers.PrimaryKeyRelatedField(
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
        read_only_fields: ClassVar = [
            "dttot_id",
            "updated_at",
            "document_data",
            "last_update_by",
        ]
