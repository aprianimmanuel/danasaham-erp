from __future__ import annotations

from typing import Any, ClassVar

from rest_framework import serializers  #type: ignore # noqa: PGH003

from app.documents.dttotDoc.dttotDocReport.models import (
    DttotDocReport,  #type: ignore # noqa: PGH003
)
from app.documents.dttotDoc.dttotDocReport.serializers import (  #type: ignore # noqa: PGH003
    dttotDocReportSerializer,
)
from app.documents.dttotDoc.dttotDocReportPersonal.models import (  #type: ignore # noqa: PGH003
    DttotDocReportPersonal,
)


class DttotDocReportPersonalSerializer(serializers.ModelSerializer):
    dttotdoc_report = serializers.PrimaryKeyRelatedField(
        queryset=DttotDocReport.objects.all(),
        required=True,
    )
    kode_densus_personal = serializers.CharField(
        required=False,
        allow_null=True,
    )
    dsb_user_personal = serializers.CharField(
        required=False,
        allow_null=True,
    )
    score_match_similarity = serializers.FloatField(
        required=False,
        allow_null=True,
    )
    dttotdoc_report_data = dttotDocReportSerializer(read_only=True, source="dttotdoc_report")

    class Meta:
        model = DttotDocReportPersonal
        fields = "__all__"
        read_only_fields: ClassVar = [
            "dttotdoc_report_data",
        ]

    def create(self, validated_data: dict[str, Any]) -> DttotDocReportPersonal:
        """Create a new instance of dttotDocReportPersonal."""
        dttotdoc_report = validated_data.pop("dttotdoc_report")

        return DttotDocReportPersonal.objects.create(dttotdoc_report=dttotdoc_report, **validated_data)

    def update(self, instance: DttotDocReportPersonal, validated_data: dict[str, Any]) -> DttotDocReportPersonal:
        """Update an existing instance of dttotDocReportPersonal."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance: DttotDocReportPersonal) -> dict[str, Any]:
        """Convert a dttotDocReportPersonal instance to a JSON representation."""
        return super().to_representation(instance)
