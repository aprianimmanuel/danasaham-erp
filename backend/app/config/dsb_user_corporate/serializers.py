from __future__ import annotations

from rest_framework import serializers

from app.config.core.models import Document, User, dsb_user_corporate
from app.config.documents.serializers import DocumentSerializer


class DsbUserCorporateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
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
        model = dsb_user_corporate
        fields = "__all__"
        read_only_fields = [
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

    def create(self, validated_data):
        user = self.context.get("request").user if self.context.get("request") else None
        validated_data["user"] = validated_data.get("user", user)
        document = validated_data.pop("document", None)
        return dsb_user_corporate.objects.create(document=document, **validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user_id"] = instance.user.user_id if instance.user else None
        representation["document_id"] = (
            instance.document.document_id if instance.document else None
        )
        return representation
