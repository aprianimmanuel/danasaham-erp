from __future__ import annotations

from typing import Any, ClassVar

from rest_framework import serializers  #type: ignore  # noqa: PGH003

from app.dttotDocReport.models import (  #type: ignore  # noqa: PGH003
    dttotDocReport,
)
from app.dttotDocReport.serializers import (  #type: ignore  # noqa: PGH003
    dttotDocReportSerializer,
)
from app.dttotDocReportCorporate.models import (  #type: ignore  # noqa: PGH003
    dttotDocReportCorporate,
)


class DttotDocReportCorporateSerializer(serializers.ModelSerializer):
    dttotdoc_report = serializers.PrimaryKeyRelatedField(
        queryset=dttotDocReport.objects.all(),
        required=True,
    )
    kode_densus_corporate = serializers.CharField(
        required=False,
        allow_null=True,
    )
    dsb_user_corporate = serializers.CharField(
        required=False,
        allow_null=True,
    )
    score_match_similarity = serializers.FloatField(
        required=False,
        allow_null=True,
    )
    dttotdoc_report_data = dttotDocReportSerializer(read_only=True, source="dttotdoc_report")

    class Meta:
        model = dttotDocReportCorporate
        fields = "__all__"
        read_only_fields: ClassVar = [
            "dttotdoc_report_data",
        ]

    def create(
            self,
            validated_data: dict[str, Any],
    ) -> dttotDocReportCorporate:
        """Create a new instance of dttotDocReportCorporate."""
        dttotdoc_report = validated_data.pop("dttotdoc_report")
        return dttotDocReportCorporate.objects.create(dttotdoc_report=dttotdoc_report, **validated_data)

    def update(
            self,
            instance: dttotDocReportCorporate,
            validated_data: dict[str, Any],
    ) -> dttotDocReportCorporate:
        """Update an existing instance of dttotDocReportCorporate."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(
            self,
            instance: dttotDocReportCorporate,
    ) -> dict[str, Any]:
        """Convert a dttotDocReportCorporate instance to a JSON representation."""
        return super().to_representation(instance)
