from __future__ import annotations

import uuid
from typing import Any, ClassVar

from django.utils import timezone
from rest_framework import serializers

from app.config.core.models import Document, User, dsb_user_personal


class DsbUserPersonalListSerializer(serializers.ModelSerializer):
    class Meta:
        model = dsb_user_personal
        fields: ClassVar = [
            "dsb_user_personal_id",
            "document",
            "coredsb_user_id",
            "user_upgrade_to_personal_date",
            "users_last_modified_date",
            "personal_legal_last_modified_date",
        ]
        read_only_fields: ClassVar = [
            "dsb_user_personal_id",
            "document",
            "coredsb_user_id",
            "user_upgrade_to_personal_date",
            "users_last_modified_date",
            "personal_legal_last_modified_date",
        ]


class DsbUserPersonalSerializer(serializers.ModelSerializer):
    """Serializer for DSB user personal data.

    It handles the creation of DSB user personal data, and the
    conversion of DSB user personal data into a JSON-serializable
    representation.
    """

    document = serializers.PrimaryKeyRelatedField(
        queryset=Document.objects.all(),
        required=True,
    )
    dsb_user_personal_id = serializers.CharField(default=uuid.uuid4)
    last_update_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
        required=False,
    )

    class Meta:
        model = dsb_user_personal
        fields = "__all__"
        read_only_fields = [  # noqa: RUF012
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

    def create(
        self, validated_data: dict[str, Any],
    ) -> dsb_user_personal:
        """Create a new instance of DSB user personal data.

        Args:
        ----
            validated_data (dict[str, Any]): The validated data for the serializer.

        Returns:
        -------
            dsb_user_personal: The newly created DSB user personal data.

        """
        # Pop the document, last_update_by and updated_date field from the validated data.
        last_update_by = validated_data.pop("last_update_by", None)
        updated_date = validated_data.pop("updated_date", None)
        document = validated_data.pop("document")

        return dsb_user_personal.objects.create(
            document=document,
            last_update_by=None,
            updated_date=None,
            **validated_data)

    def update(
        self, instance: dsb_user_personal, validated_data: dict[str, Any],
    ) -> dsb_user_personal:
        """Update an existing instance of DSB user personal data.

        Args:
        ----
            instance (dsb_user_personal): The existing DSB user personal data.
            validated_data (dict[str, Any]): The validated data for the serializer.

        Returns:
        -------
            dsb_user_personal: The updated DSB user personal data.

        """
        user = self.context.get("request").user if self.context.get("request") else None
        instance.last_update_by = user
        instance.updated_date = timezone.now
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
    def to_representation(
        self, instance: dsb_user_personal,
    ) -> dict[str, Any]:
        """Convert DSB user personal data into a JSON-serializable representation.

        Args:
        ----
            instance (dsb_user_personal): The DSB user personal data.

        Returns:
        -------
            dict[str, Any]: The JSON-serializable representation of DSB user personal data.

        """
        representation = super().to_representation(instance)
        representation["last_update_by"] = instance.last_update_by.user_id if instance.last_update_by else None
        return representation
