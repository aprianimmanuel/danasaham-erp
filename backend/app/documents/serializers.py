from __future__ import annotations

import uuid
from typing import Any, ClassVar

from django.utils import timezone  #type: ignore  # noqa: PGH003
from rest_framework import serializers  #type: ignore  # noqa: PGH003

from app.documents.models import Document  #type: ignore  # noqa: PGH003
from app.user.models import User  #type: ignore  # noqa: PGH003


class DocumentSerializer(serializers.ModelSerializer):
    document_name = serializers.CharField(required=True)
    description = serializers.CharField(allow_blank=True, required=False)
    document_file = serializers.FileField(required=False)
    document_file_type = serializers.CharField(required=False)
    document_type = serializers.CharField(required=True)
    created_date = serializers.DateTimeField(default=timezone.now, read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
        required=False)
    last_update_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
        required=False)
    document_id = serializers.CharField(
        default=uuid.uuid4,
        required=False,
        read_only=True,
    )
    last_update_date = serializers.DateTimeField(
        default=timezone.now,
        read_only=True,
    )
    letter_number = serializers.CharField(required=False)
    dttot_letter_number_reference = serializers.CharField(required=False)
    police_letter_date = serializers.CharField(required=False)
    police_letter_about = serializers.CharField(required=False)
    police_letter_number = serializers.CharField(required=False)

    class Meta:
        model = Document
        fields = "__all__"
        read_only_fields: ClassVar = [
            "created_date",
            "document_id",
            "last_update_date",
            "last_update_by",
            "created_by",
            "updated_by",
        ]
        extra_kwargs = {  # noqa: RUF012
            "created_by": {"default": serializers.CurrentUserDefault()},
            "updated_by": {"default": serializers.CurrentUserDefault()},
        }

    def validate_document_file(self, data: dict[str, Any]) -> dict[str, Any]:
        if data.get("document_type") == "DTTOT Report" and not data.get("document_file"):
            raise serializers.ValidationError({"document_file": "This field is required for DTTOT Report documents."})
        return data

    def validate_dttot_letter_number_reference(self, data: dict[str, Any]) -> dict[str, Any]:
        if data.get("document_type") == "DTTOT Report" and not data.get("dttot_letter_number_reference"):
            raise serializers.ValidationError({"dttot_letter_number_reference": "This field is required for DTTOT Report documents."})
        return data

    def validate_police_letter_date(self, data: dict[str, Any]) -> dict[str, Any]:
        if data.get("document_type") == "DTTOT Report" and not data.get("police_letter_date"):
            raise serializers.ValidationError({"police_letter_date": "This field is required for DTTOT Report documents."})
        return data

    def validate_police_letter_about(self, data: dict[str, Any]) -> dict[str, Any]:
        if data.get("document_type") == "DTTOT Report" and not data.get("police_letter_about"):
            raise serializers.ValidationError({"police_letter_about": "This field is required for DTTOT Report documents."})
        return data

    def validate_police_letter_number(self, data: dict[str, Any]) -> dict[str, Any]:
        if data.get("document_type") == "DTTOT Report" and not data.get("police_letter_number"):
            raise serializers.ValidationError({"police_letter_number": "This field is required for DTTOT Report documents."})
        return data

    def validate_sequence_number(self, data: dict[str, Any]) -> dict[str, Any]:
        if data.get("document_type") == "DTTOT Report" and not data.get("sequence_number"):
            raise serializers.ValidationError({"sequence_number": "This field is required for DTTOT Report documents."})
        return data

    def validate_document_type(self, data: dict[str, Any]) -> dict[str, Any]:
        if data.get("document_type") == "DTTOT Report" and not data.get("document_file_type"):
            raise serializers.ValidationError({"document_file_type": "This field is required for DTTOT Report documents."})
        return data

    def create(self, validated_data: dict[str, Any]) -> Document:
        """Create a new document instance.

        Args:
        ----
            validated_data (dict[str, Any]): The validated data for creating a new document.

        Returns:
        -------
            Document: The newly created document instance.

        """
        # If the request context exists and the user is authenticated,
        # assign the authenticated user to the created_by field.
        request = self.context.get("request", None)
        if request and request.user.is_authenticated:
            validated_data["created_by"] = request.user

        # Create the document instance. The document_file will be saved automatically.
        return Document.objects.create(**validated_data)

    def update(
            self: DocumentSerializer,
            instance: Document,
            validated_data: dict[str, Any],
    ) -> Document:
        """Update an existing document instance.

        Args:
        ----
            instance (Document): The existing document instance to update.
            validated_data (dict[str, Any]): The validated data for the serializer.

        Returns:
        -------
            Document: The updated document instance.

        """
        # If the request context exists and the user is authenticated,
        # assign the authenticated user to the last_update_by field.
        request = self.context.get("request", None)
        if request and request.user.is_authenticated:
            validated_data["last_update_by"] = request.user
            validated_data["last_update_date"] = timezone.now()
        return super().update(instance, validated_data)

    def to_representation(
        self,
        instance: Any,
    ) -> dict[str, Any]:
        """Convert a Document instance to a JSON-serializable representation.

        Args:
        ----
            instance (Document): The Document instance to convert.

        Returns:
        -------
            dict[str, Any]: The JSON-serializable representation of the Document instance.

        """
        representation = super().to_representation(instance)
        if instance.document_file:
            representation["document_file"] = instance.document_file.url
        return representation
