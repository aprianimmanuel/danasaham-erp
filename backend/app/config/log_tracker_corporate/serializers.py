from __future__ import annotations

from typing import Any, ClassVar

from django.utils import timezone
from rest_framework import serializers

from app.config.core.models import Document, User, log_tracker_corporate


class LogTrackerCorporateListSerializer(serializers.ModelSerializer):
    document = serializers.PrimaryKeyRelatedField(
        queryset=Document.objects.all(),
        required=True,
    )
    log_tracker_corporate_id = serializers.CharField(read_only=True)

    class Meta:
        model = log_tracker_corporate
        fields: ClassVar = [
            "document",
            "log_tracker_corporate_id",
            "core_dsb_user_id",
            "created_date",
            "updated_date",
            "last_update_by",
            "initial_registration_date",
        ]

class LogTrackerCorporateSerializer(serializers.ModelSerializer):
    last_update_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
        required=False,
    )
    document = serializers.PrimaryKeyRelatedField(
        queryset=Document.objects.all(),
        required=True,
    )
    log_tracker_corporate_id = serializers.CharField(read_only=True)

    class Meta:
        model = log_tracker_corporate
        fields = "__all__"
        read_only_fields = [  # noqa: RUF012
            "log_tracker_corporate_id",
            "created_date",
            "updated_date",
            "last_update_by",
            "initial_registration_date",
        ]

    def create(
        self,
        validated_data: dict[str, Any],
    ) -> log_tracker_corporate:
        """Create a new log_tracker_corporate instance."""
        log_tracker_corporate.objects.create(**validated_data)

    def update(
        self,
        instance: log_tracker_corporate,
        validated_data: dict[str, Any],
    ) -> log_tracker_corporate:
        """Update an existing log_tracker_corporate instance.

        Args:
        ----
            instance: The log_tracker_corporate instance to update.
            validated_data: The validated data to update the instance with.

        Returns:
        -------
            The updated log_tracker_corporate instance.

        """
        # Set the user field to the authenticated user if available.
        validated_data["last_update_by"] = validated_data.pop("last_update_by")

        # Set the last_update_date field to the current time.
        validated_data["updated_date"] = timezone.now()

        # Update the instance with the validated data
        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        return instance

    def to_representation(
            self,
            instance: log_tracker_corporate,
    ) -> dict[str, Any]:
        """Convert the log_tracker_corporate instance to a dictionary representation.

        Args:
        ----
            instance: The log_tracker_corporate instance to convert.

        Returns:
        -------
            A dictionary representation of the log_tracker_corporate instance.

        """
        return super().to_representation(
            instance,
    )
