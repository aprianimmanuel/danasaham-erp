from __future__ import annotations

from typing import Any

from django.utils import timezone
from rest_framework import serializers

from app.config.core.models import Document, User, dsb_user_publisher


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
        model = dsb_user_publisher
        fields = "__all__"
        read_only_fields = [  # noqa: RUF012
            "dsb_user_publisher_id",
            "created_date",
            "updated_date",
            "last_update_by",
            "initial_registration_date",
            "coredsb_user_id",
            "user_name",
            "registered_user_email",
            "users_phone_number",
            "users_last_modified_date",
            "user_upgrade_to_publisher_date",
            "publisher_registered_name",
            "publisher_corporate_type",
            "publisher_phone_number",
            "publisher_business_field",
            "publisher_main_business",
            "domicile_address_publisher_1",
            "domicile_address_publisher_2",
            "domicile_address_publisher_3_city",
            "publisher_last_modified_date",
            "publisher_pengurus_id",
            "publisher_pengurus_name",
            "publisher_pengurus_id_number",
            "publisher_pengurus_role_as",
            "publisher_jabatan_pengurus",
            "publisher_address_pengurus",
            "publisher_tgl_lahir_pengurus",
            "publisher_tempat_lahir_pengurus",
            "pengurus_publisher_last_modified_date",
        ]

    def create(
        self,
        validated_data: dict[str, Any],
    ) -> dsb_user_publisher:
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
        return dsb_user_publisher.objects.create(
            document=document,
            last_update_by=None,
            updated_date=None,
            **validated_data)

    def update(
        self,
        instance: dsb_user_publisher,
        validated_data: dict[str, Any],
    ) -> dsb_user_publisher:
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
            instance: dsb_user_publisher,
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
