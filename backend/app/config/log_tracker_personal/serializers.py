from __future__ import annotations

from typing import Any

from django.utils import timezone
from rest_framework import serializers

from app.config.core.models import Document, User, log_tracker_personal


class LogTrackerPersonalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = log_tracker_personal
        fields = [  # noqa: RUF012
            "log_tracker_personal_id",
            "core_dsb_user_id",
            "created_date",
            "updated_date",
            "last_update_by",
            "initial_registration_date",
        ]

class LogTrackerPersonalSerializer(serializers.ModelSerializer):
    last_update_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
        required=False,
    )
    document = serializers.PrimaryKeyRelatedField(
        queryset=Document.objects.all(),
        required=True,
    )
    log_tracker_personal_id = serializers.CharField(read_only=True)

    class Meta:
        model = log_tracker_personal
        fields = "__all__"
        read_only_fields = [  # noqa: RUF012
            "log_tracker_personal_id",
            "created_date",
            "updated_date",
            "last_update_by",
            "initial_registration_date",
        ]

    def create(
        self,
        validated_data: dict[str, Any],
    ) -> log_tracker_personal:
        """Create a new log_tracker_personal instance."""
        log_tracker_personal.objects.create(**validated_data)

    def update(
        self,
        instance: log_tracker_personal,
        validated_data: dict[str, Any],
    ) -> log_tracker_personal:
        """Update an existing log_tracker_personal instance.

        Args:
        ----
            instance (log_tracker_personal): The existing log_tracker_personal instance to update.
            validated_data (dict[str, Any]): The validated data for the serializer.

        Returns:
        -------
            log_tracker_personal: The updated log_tracker_personal instance.

        """
        # Set the user field to the authenticated user if available.
        validated_data["last_update_by"] = validated_data.pop("last_update_by")

        # Set the last_updated_date to the current time
        validated_data["last_updated_date"] = timezone.now()

        # Update the log_tracker_personal instance
        return super().update(instance, validated_data)


    def to_representation(
        self,
        instance: log_tracker_personal,
    ) -> dict[str, Any]:
        """Convert the log_tracker_personal instance to a dictionary representation.

        Args:
        ----
            instance (log_tracker_personal): The log_tracker_personal instance to convert.

        Returns:
        -------
            dict[str, Any]: A dictionary representation of the log_tracker_personal instance.

        """
        return super().to_representation(instance)
