from __future__ import annotations

from typing import Any

from rest_framework import serializers  #type: ignore # noqa: PGH003

from app.documents.models import Document  #type: ignore # noqa: PGH003
from app.dsb_user.dsb_user_corporate.models import (  #type: ignore # noqa: PGH003
    DsbUserCorporate,
)
from app.user.models import User  #type: ignore # noqa: PGH003


class DsbUserCorporateListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DsbUserCorporate
        fields = "__all__"
        read_only_fields = "__all__"

class DsbUserCorporateSerializer(serializers.ModelSerializer):
    document = serializers.PrimaryKeyRelatedField(
        queryset=Document.objects.all(),
        required=True,
    )
    last_update_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
    )
    class Meta:
        model = DsbUserCorporate
        fields = "__all__"
        read_only_fields = "__all__"

    def create(
            self: DsbUserCorporateSerializer,
            validated_data: dict[str, Any],
    ) -> DsbUserCorporate:
        """Create a new instance of DSB user corporate data.

        Args:
        ----
            self (DsbUserCorporateSerializer): The serializer instance.
            validated_data (dict[str, Any]): The validated data for creating a new instance.

        Returns:
        -------
            dsb_user_corporate: The newly created DSB user corporate data.

        """
        # Pop the document, last_update_by and updated_date field from the validated data.
        document = validated_data.pop("document")

        # Create a new instance of dsb_user_corporate using the validated data.
        return DsbUserCorporate.objects.create(
            document=document,
            last_update_by=None,
            updated_date=None,
            **validated_data)

    def update(
            self: DsbUserCorporateSerializer,
            instance: DsbUserCorporate,
            validated_data: dict[str, Any],
    ) -> DsbUserCorporate:
        """Update an existing instance of DSB user corporate data.

        Args:
        ----
            instance (dsb_user_corporate): The existing DSB user corporate data.
            validated_data (dict[str, Any]): The validated data for updating the instance.

        Returns:
        -------
            dsb_user_corporate: The updated DSB user corporate data.

        """
        document: Document | None = validated_data.pop("document", None)
        last_update_by: User | None = validated_data.pop("last_update_by", None)

        return super().update(instance, validated_data)

    def to_representation(
            self: DsbUserCorporateSerializer,
            instance: DsbUserCorporate,
    ) -> dict[str, Any]:
        """Convert DSB user corporate data into a JSON-serializable representation.

        Args:
        ----
            instance (dsb_user_corporate): The DSB user corporate data.

        Returns:
        -------
            dict[str, Any]: The JSON-serializable representation of DSB user corporate data.
                The dictionary contains the following keys:
                - document_id: The ID of the document associated with the instance, or None.

        """
        # Get the parent class's representation of the instance.
        representation: dict[str, Any] = super().to_representation(instance)

        # Add the last_update_by field to the representation.
        representation["last_update_by"] = (
            instance.last_update_by.user_id if instance.last_update_by else None
        )

        # Return the representation.
        return representation
