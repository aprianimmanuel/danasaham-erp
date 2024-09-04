from __future__ import annotations

from typing import Any

from rest_framework import serializers

from app.config.core.models import Document, User, dsb_user_corporate


class DsbUserCorporateListSerializer(serializers.ModelSerializer):
    model = dsb_user_corporate
    fields = [  # noqa: RUF012
        "dsb_user_corporate_id",
        "document",
        "last_update_by",
        "created_date",
        "updated_date",
        "corporate_pengurus_id",
    ]

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
        model = dsb_user_corporate
        fields = [  # noqa: RUF012
            "dsb_user_corporate_id",
            "created_date",
            "updated_date",
            "last_update_by",
            "initial_registration_date",
            "user_name",
            "registered_user_email",
            "users_phone_number",
            "coredsb_user_id",
            "users_upgrade_to_corporate",
            "users_last_modified_date",
            "corporate_pengurus_id",
            "pengurus_corporate_name",
            "pengurus_corporate_id_number",
            "pengurus_corporate_phone_number",
            "pengurus_corporate_place_of_birth",
            "pengurus_corporate_date_of_birth",
            "pengurus_corporate_npwp",
            "pengurus_corporate_domicile_address",
            "pengurus_nominal_saham",
            "pengurus_corporate_last_update_date",
            "corporate_company_name",
            "corporate_phone_number",
            "corporate_nib",
            "corporate_npwp",
            "corporate_siup",
            "corporate_skdp",
            "corporate_domicile_address",
            "corporate_asset",
            "corporate_source_of_fund",
            "corporate_business_field",
            "corporate_type_of_annual_income",
            "corporate_annual_income",
            "corporate_investment_goals",
            "corporate_legal_last_modified_date",
        ]
        read_only_fields = [  # noqa: RUF012
            "dsb_user_corporate_id",
            "created_date",
            "updated_date",
            "last_update_by",
            "initial_registration_date",
            "user_name",
            "registered_user_email",
            "users_phone_number",
            "coredsb_user_id",
            "users_upgrade_to_corporate",
            "users_last_modified_date",
            "corporate_pengurus_id",
            "pengurus_corporate_name",
            "pengurus_corporate_id_number",
            "pengurus_corporate_phone_number",
            "pengurus_corporate_place_of_birth",
            "pengurus_corporate_date_of_birth",
            "pengurus_corporate_npwp",
            "pengurus_corporate_domicile_address",
            "pengurus_nominal_saham",
            "pengurus_corporate_last_update_date",
            "corporate_company_name",
            "corporate_phone_number",
            "corporate_nib",
            "corporate_npwp",
            "corporate_siup",
            "corporate_skdp",
            "corporate_domicile_address",
            "corporate_asset",
            "corporate_source_of_fund",
            "corporate_business_field",
            "corporate_type_of_annual_income",
            "corporate_annual_income",
            "corporate_investment_goals",
            "corporate_legal_last_modified_date",
        ]

    def create(
            self: DsbUserCorporateSerializer,
            validated_data: dict[str, Any],
    ) -> dsb_user_corporate:
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
        last_update_by = validated_data.pop("last_update_by", None)
        updated_date = validated_data.pop("updated_date", None)
        document = validated_data.pop("document")

        # Create a new instance of dsb_user_corporate using the validated data.
        return dsb_user_corporate.objects.create(
            document=document,
            last_update_by=None,
            updated_date=None,
            **validated_data)

    def update(
            self: DsbUserCorporateSerializer,
            instance: dsb_user_corporate,
            validated_data: dict[str, Any],
    ) -> dsb_user_corporate:
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
            instance: dsb_user_corporate,
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

        # Add the document_data field to the representation.
        representation["document_data"] = instance.document.document_id

        # Return the representation.
        return representation
