from __future__ import annotations

from typing import Any, ClassVar

from django.utils import timezone
from rest_framework import serializers

from app.config.core.models import Document, User, log_tracker_publisher
from app.config.documents.serializers import DocumentSerializer


class LogTrackerPublisherListSerializer(serializers.ModelSerializer):
    document = serializers.PrimaryKeyRelatedField(
        queryset=Document.objects.all(),
        required=True,
    )
    log_tracker_publisher_id = serializers.CharField(read_only=True)

    class Meta:
        model = log_tracker_publisher
        fields: ClassVar = [
            "document",
            "log_tracker_publisher_id",
            "core_dsb_user_id",
            "created_date",
            "last_updated_date",
            "last_update_by",
            "initial_registration_date",
        ]
        read_only_fields: ClassVar = [
            "document",
            "log_tracker_publisher_id",
            "core_dsb_user_id"
            "created_date",
            "last_updated_date",
            "last_update_by",
            "initial_registration_date",
        ]

class LogTrackerPublisherSerializer(serializers.ModelSerializer):
    last_update_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
        required=False,
    )
    document = serializers.PrimaryKeyRelatedField(
        queryset=Document.objects.all(),
        required=True,
    )
    log_tracker_publisher_id = serializers.CharField(read_only=True)
    document_data = DocumentSerializer(read_only=True, source="document")

    class Meta:
        model = log_tracker_publisher
        fields = "__all__"
        read_only_fields = [  # noqa: RUF012
            "log_tracker_publisher_id",
            "created_date",
            "last_updated_date",
            "last_update_by",
            "initial_registration_date",
            "document_data",
        ]

    def create(self, validated_data: dict[str, Any]) -> log_tracker_publisher:
        """Create a new log_tracker_publisher instance."""
        log_tracker_publisher.objects.create(**validated_data)

    def update(
        self: LogTrackerPublisherSerializer,
        instance: log_tracker_publisher,
        validated_data: dict[str, Any],
    ) -> log_tracker_publisher:
        """Update an existing log_tracker_publisher instance.

        Args:
        ----
            instance (log_tracker_publisher): The existing log_tracker_publisher instance to update.
            validated_data (dict[str, Any]): The validated data for the serializer.

        Returns:
        -------
            log_tracker_publisher: The updated log_tracker_publisher instance.

        """
        # Set the user field to the authenticated user if available.
        validated_data["last_update_by"] = validated_data.pop("last_update_by")

        # Set last_updated_date to the current time.
        validated_data["last_updated_date"] = timezone.now()

        return super().update(instance, validated_data)

    def to_representation(
        self: LogTrackerPublisherSerializer,
        instance: log_tracker_publisher,
    ) -> dict[str, Any]:
        """Convert a log_tracker_publisher instance to a JSON-serializable representation.

        Args:
        ----
            instance (log_tracker_publisher): The log_tracker_publisher instance to convert.

        Returns:
        -------
            Dict[str, Any]: A JSON-serializable representation of the log_tracker_publisher instance.

        """
        # Get the parent class's representation of the instance.
        representation = super().to_representation(instance)

        # Add the document_id field to the representation.
        representation["document_id"] = instance.document.document_id

        # Return the representation.
        return super().to_representation(instance)
