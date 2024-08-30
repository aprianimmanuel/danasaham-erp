from __future__ import annotations

import logging
from typing import Any, ClassVar

from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from app.common.routers import CustomViewRouter
from app.config.core.models import dttotDocReport
from app.config.dttotDocReport.serializers import dttotDocReportSerializer

logger = logging.getLogger(__name__)

router = CustomViewRouter(url_prefix="api/")

@router.register_decorator(
    r"documents/dttotReport/list/",
    name="dttot-report-list",
)
class dttotDocReportView(generics.ListAPIView):  # noqa: N801
    serializer_class = dttotDocReportSerializer
    permission_classes: ClassVar[list[type[permissions.BasePermission]]] = [permissions.IsAuthenticated]
    queryset = dttotDocReport.objects.all()

@router.register_decorator(
    r"documents/dttotReport/details/$",
    name="dttot-report-detail",
)
class dttotDocReportDetailView(GenericAPIView):  # noqa: N801
    serializer_class = dttotDocReportSerializer
    permission_classes: ClassVar[list[type[permissions.BasePermission]]] = [permissions.IsAuthenticated]

    @extend_schema(responses={200: dttotDocReportSerializer})
    def get(self, _request: Any) -> Response:
        """To fetche the DTTOT Report document details for a specific DTTOT Report document ID."""
        # Retrieving identifier from query params
        dttotdoc_report_id = _request.query_params.get("identifier")
        if not dttotdoc_report_id:
            return Response(
                {"detail": "Identifier query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST)

        # Logging the fetch operation
        logger.info(
            "Fetching DTTOT Report document details for DTTOT Report ID: %s",
            dttotdoc_report_id,
        )

        try:
            # Fetching the DTTOT Report document
            dttot_doc_report = dttotDocReport.objects.get(
                dttotdoc_report_id=dttotdoc_report_id,
            )
        except dttotDocReport.DoesNotExist:
            return Response(
                {"detail": "DTTOT Report document not found."},
                status=status.HTTP_404_NOT_FOUND)

        # Serializing the fetched document
        serializer = self.get_serializer(dttot_doc_report)

        # Logging the successful fetch operation
        logger.info(
            "Successfully fetched DTTOT Report document details for DTTOT Report ID: %s",
            dttotdoc_report_id,
        )

        # Returning the serialized document data in the response
        return Response(serializer.data)

    @extend_schema(
        request=dttotDocReportSerializer,
        responses={200: dttotDocReportSerializer},
    )
    def put(self, request: Any) -> Response:
        """To update the DTTOT Report document for a specific DTTOT Report document ID."""
        # Retrieving identifier from query params
        dttotdoc_report_id = request.query_params.get("identifier")
        if not dttotdoc_report_id:
            return Response(
                {"detail": "Identifier query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST)

        # Logging the update operation
        logger.info(
            "Updating DTTOT Report document for DTTOT Report ID: %s",
            dttotdoc_report_id,
        )

        try:
            # Fetching the DTTOT Report document
            dttot_doc_report = dttotDocReport.objects.get(
                dttotdoc_report_id=dttotdoc_report_id,
            )
        except dttotDocReport.DoesNotExist:
            return Response(
                {"detail": "DTTOT Report document not found."},
                status=status.HTTP_404_NOT_FOUND)

        # Updating the DTTOT Report document
        serializer = self.get_serializer(dttot_doc_report, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(
                "Successfully updated DTTOT Report document for DTTOT Report ID: %s",
                dttotdoc_report_id,
            )
            return Response(
                {"detail": "DTTOT Report document successfully updated!", "data": serializer.data},
                status=status.HTTP_200_OK)

        return Response(
            {"detail": "Failed to update DTTOT Report document.", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="Deletes the DTTOT Report document for a specific DTTOT Report document ID.",
        responses={204: None},
    )
    def delete(self, _request: Any) -> Response:
        """To delete the DTTOT Report document for a specific DTTOT Report document ID."""
        # Retrieving identifier from query params
        dttotdoc_report_id = _request.query_params.get("identifier")
        if not dttotdoc_report_id:
            return Response(
                {"detail": "Identifier query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST)

        # Logging the delete operation
        logger.info(
            "Deleting DTTOT Report document for DTTOT Report ID: %s",
            dttotdoc_report_id,
        )

        try:
            # Fetching the DTTOT Report document
            dttot_doc_report = dttotDocReport.objects.get(
                dttotdoc_report_id=dttotdoc_report_id,
            )
        except dttotDocReport.DoesNotExist:
            return Response(
                {"detail": "DTTOT Report document not found."},
                status=status.HTTP_404_NOT_FOUND)

        # Deleting the DTTOT Report document
        dttot_doc_report.delete()

        # Logging the successful delete operation
        logger.info(
            "Successfully deleted DTTOT Report document for DTTOT Report ID: %s",
            dttotdoc_report_id,
        )

        # Returning a no content response
        return Response(
            {"detail": "DTTOT Report document has been successfully deleted!"},
            status=status.HTTP_204_NO_CONTENT)

    @extend_schema(responses={200: dttotDocReportSerializer})
    def patch(self, _request: Any) -> Response:
        """To partially update the DTTOT Report document for a specific DTTOT Report document ID."""
        # Retrieving identifier from query params
        dttotdoc_report_id = _request.query_params.get("identifier")
        if not dttotdoc_report_id:
            return Response(
                {"detail": "Identifier query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST)

        # Logging the partial update operation
        logger.info(
            "Patching DTTOT Report document for DTTOT Report ID: %s",
            dttotdoc_report_id,
        )

        try:
            # Fetching the DTTOT Report document
            dttot_doc_report = dttotDocReport.objects.get(
                dttotdoc_report_id=dttotdoc_report_id,
            )
        except dttotDocReport.DoesNotExist:
            return Response(
                {"detail": "DTTOT Report document not found."},
                status=status.HTTP_404_NOT_FOUND)

        # Initializing the serializer with the fetched document and request data
        serializer = self.get_serializer(
            dttot_doc_report, data=_request.data, partial=True,
        )

        # Checking if the serializer is valid
        if serializer.is_valid():
            serializer.save()

            # Logging the successful partial update operation
            logger.info(
                "Successfully patched DTTOT Report document for DTTOT Report ID: %s",
                dttotdoc_report_id,
            )

            # Returning the updated document data in the response
            return Response(
                {"detail": "DTTOT Report document successfully patched!", "data": serializer.data},
                status=status.HTTP_200_OK)

        return Response(
            {"detail": "Failed to patch DTTOT Report document.", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST)
