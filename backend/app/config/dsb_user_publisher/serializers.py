from __future__ import annotations

from rest_framework import serializers

from app.config.core.models import Document, User, dsb_user_publisher
from app.config.documents.serializers import DocumentSerializer


class DsbUserPublisherSerializer(serializers.ModelSerializer):
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
        model = dsb_user_publisher
        fields = "__all__"
        read_only_fields = [
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

    def create(self,validated_data):
        user = self.context.get("request").user if self.context.get("request") else None
        validated_data["user"] = validated_data.get("user", user)
        document = validated_data.pop("document", None)
        return dsb_user_publisher.objects.create(document=document, **validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user_id"] = instance.user.user_id if instance.user else None
        representation["document_id"] = (
            instance.document.document_id if instance.document else None
        )
        return representation
