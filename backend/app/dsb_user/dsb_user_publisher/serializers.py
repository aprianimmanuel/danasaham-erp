from __future__ import annotations

from typing import Any, ClassVar

from django.utils import timezone  #type: ignore # noqa: PGH003
from rest_framework import serializers  #type: ignore # noqa: PGH003

from app.documents.models import Document  #type: ignore # noqa: PGH003
from app.dsb_user.dsb_user_publisher.models import (  #type: ignore # noqa: PGH003
    DsbUserPublisher,
)
from app.user.models import User  #type: ignore # noqa: PGH003


class DsbUserPublisherListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DsbUserPublisher
        fields: ClassVar = "__all__"
        read_only_fields: ClassVar = "__all__"

class DsbUserPublisherSerializer(serializers.ModelSerializer):
    document = serializers.PrimaryKeyRelatedField(
        queryset=Document.objects.all(),
        required=True,
    )
    last_update_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
        required=False,
    )
    dsb_user_publisher_id = serializers.CharField(read_only=True)

    class Meta:
        model = DsbUserPublisher
        fields = "__all__"
        read_only_fields = "__all__"

    def create(
        self,
        validated_data: dict[str, Any],
    ) -> DsbUserPublisher:
        """Create a new instance of dsb_user_publisher.

        This function creates a new instance of dsb_user_publisher using the validated data.
        It also sets the user field to the authenticated user if available.

        Args:
        ----
            validated_data (Dict[str, Any]): The validated data for creating a new instance.

        Returns:
        -------
            dsb_user_publisher: The newly created dsb_user_publisher instance.

        """
        # Pop the document, last_update_by and updated_date field from the validated data.
        last_update_by = validated_data.pop("last_update_by", None)
        updated_date = validated_data.pop("updated_date", None)
        document = validated_data.pop("document")

        # Create a new instance of dsb_user_publisher using the validated data.
        return DsbUserPublisher.objects.create(
            document=document,
            last_update_by=None,
            updated_date=None,
            **validated_data)

    def update(
        self,
        instance: DsbUserPublisher,
        validated_data: dict[str, Any],
    ) -> DsbUserPublisher:
        """Update an existing instance of dsb_user_publisher.

        This function updates an existing instance of dsb_user_publisher using the validated data.
        It also sets the user field to the authenticated user if available.

        Args:
        ----
            instance (dsb_user_publisher): The existing dsb_user_publisher instance to update.
            validated_data (Dict[str, Any]): The validated data for updating the instance.

        Returns:
        -------
            dsb_user_publisher: The updated dsb_user_publisher instance.

        """
        # Set the user field to the authenticated user if available.
        user = self.context.get("request").user if self.context.get("request") else None

        instance.last_update_by = user
        instance.updated_date = timezone.now

        # Update the instance of dsb_user_publisher using the validated data.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

    def to_representation(
            self,
            instance: DsbUserPublisher,
        ) -> dict[str, Any]:
        """Convert a DsbUserPublisher instance to a JSON-serializable representation.

        Args:
        ----
            instance (DsbUserPublisher): The DsbUserPublisher instance to convert.

        Returns:
        -------
            dict[str, Any]: The JSON-serializable representation of the DsbUserPublisher instance.
                The dictionary contains the following keys:
                - user_id: The ID of the user associated with the instance, or None.
                - document_id: The ID of the document associated with the instance, or None.

        """
        # Get the parent class's representation of the instance.
        representation: dict[str, Any] = super().to_representation(instance)

        # Add the user_id and document_id fields to the representation.
        representation["last_update_by"] = instance.last_update_by.user_id if instance.last_update_by else None
        representation["document_data"] = instance.document.document_id

        # Return the representation.
        return representation
