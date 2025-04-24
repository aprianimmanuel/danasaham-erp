from __future__ import annotations

from typing import Any, ClassVar

from rest_framework import serializers  #type: ignore # noqa: PGH003

from app.documents.dttotDoc.dttotDocReport.models import (
    DttotDocReport,  #type: ignore # noqa: PGH003
)
from app.documents.dttotDoc.dttotDocReport.serializers import (  #type: ignore # noqa: PGH003
    dttotDocReportSerializer,
)
from app.documents.dttotDoc.dttotDocReportPublisher.models import (  #type: ignore # noqa: PGH003
    DttotDocReportPublisher,
)


class DttotDocReportPublisherSerializer(serializers.ModelSerializer):
    dttotdoc_report = serializers.PrimaryKeyRelatedField(
        queryset=DttotDocReport.objects.all(),
        required=True,
    )
    kode_densus_publisher = serializers.CharField(
        required=False,
        allow_null=True,
    )
    dsb_user_publisher = serializers.CharField(
        required=False,
        allow_null=True,
    )
    score_match_similarity = serializers.FloatField(
        required=False,
        allow_null=True,
    )
    dttotdoc_report_data = dttotDocReportSerializer(read_only=True, source="dttotdoc_report")

    class Meta:
        model = DttotDocReportPublisher
        fields = "__all__"
        read_only_fields: ClassVar = [
            "dttotdoc_report_data",
        ]

    def create(
            self,
            validated_data: dict[str, Any],
    ) -> DttotDocReportPublisher:
        """Create a new instance of dttotDocReportPublisher."""
        dttotdoc_report = validated_data.pop("dttotdoc_report")

        return DttotDocReportPublisher.objects.create(dttotdoc_report=dttotdoc_report, **validated_data)

    def update(
            self,
            instance: DttotDocReportPublisher,
            validated_data: dict[str, Any],
    ) -> DttotDocReportPublisher:
        """Update an existing instance of dttotDocReportPublisher."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(
            self,
            instance: DttotDocReportPublisher,
    ) -> dict[str, Any]:
        """Convert a dttotDocReportPublisher instance to a JSON representation."""
        return super().to_representation(instance)
