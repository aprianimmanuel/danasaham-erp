from __future__ import annotations

import uuid
from typing import Any, ClassVar

from django.utils import timezone  #type: ignore # noqa: PGH003
from rest_framework import serializers  #type: ignore # noqa: PGH003

from app.documents.dttotDoc.dttotDocReport.models import (
    DttotDocReport,  #type: ignore # noqa: PGH003
)
from app.documents.models import Document  #type: ignore # noqa: PGH003
from app.documents.serializers import DocumentSerializer  #type: ignore # noqa: PGH003
from app.user.models import User  #type: ignore # noqa: PGH003


class dttotDocReportSerializer(serializers.ModelSerializer):  # noqa: N801
    document = serializers.PrimaryKeyRelatedField(
        queryset=Document.objects.all(),
        required=True,
    )
    dttodoc_report_id = serializers.CharField(
        default=uuid.uuid4,
        max_length=36,
        read_only=True,
    )
    last_update_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
    )
    updated_date = serializers.DateTimeField(read_only=True, allow_null=True)
    status_doc = serializers.CharField(read_only=True, allow_null=True)
    document_data = DocumentSerializer(read_only=True, source="document")


    class Meta:
        model = DttotDocReport
        fields = "__all__"
        read_only_fields: ClassVar = [
            "dttotdoc_report_id",
            "last_update_by",
            "created_date",
            "updated_date",
            "status_doc",
            "document_data",
        ]

    def create(self, validated_data: dict[str, Any]) -> DttotDocReport:
        """Create a new instance of a dttotDocReport."""
        return DttotDocReport.objects.create(**validated_data)


    def update(self, instance: DttotDocReport, validated_data: dict[str, Any]) -> DttotDocReport:
        """Update an existing instance of a dttotDocReport."""
        request = self.context.get("request")
        validated_data["updated_date"] = timezone.now()
        validated_data["last_update_by"] = request.user if request else None

        return super().update(instance, validated_data)

    def to_representation(self, instance: DttotDocReport) -> dict[str, Any]:
        """Convert a dttotDocReport instance into a JSON-serializable representation."""
        return super().to_representation(instance)


