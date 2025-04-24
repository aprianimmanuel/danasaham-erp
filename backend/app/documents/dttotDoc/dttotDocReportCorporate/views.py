from __future__ import annotations

import logging
from typing import Any, ClassVar

from drf_spectacular.utils import extend_schema  #type: ignore # noqa: PGH003
from rest_framework import generics, permissions, status  #type: ignore # noqa: PGH003
from rest_framework.generics import GenericAPIView  #type: ignore # noqa: PGH003
from rest_framework.response import Response  #type: ignore # noqa: PGH003

from app.common.routers import CustomViewRouter  #type: ignore # noqa: PGH003
from app.documents.dttotDoc.dttotDocReportCorporate.models import (  #type: ignore # noqa: PGH003
    DttotDocReportCorporate,
)
from app.documents.dttotDoc.dttotDocReportCorporate.serializers import (  #type: ignore # noqa: PGH003
    DttotDocReportCorporateSerializer,
)

logger = logging.getLogger(__name__)

router = CustomViewRouter(url_prefix="api/")

@router.register_decorator(
    r"documents/dttotdocreport/dttotReportCorporate/list/",
    name="dttot-report-corporate-list",
)
class dttotDocReportCorporateView(generics.ListAPIView):  # noqa: N801
    serializer_class = DttotDocReportCorporateSerializer
    permission_classes: ClassVar[list[type[permissions.BasePermission]]] = [permissions.IsAuthenticated]
    queryset = DttotDocReportCorporate.objects.all()

@router.register_decorator(
    r"documents/dttotdocreport/dttotReportCorporate/details/$",
    name="dttot-report-corporate-detail",
)
class dttotDocReportCorporateDetailView(GenericAPIView):  # noqa: N801
    serializer_class = DttotDocReportCorporateSerializer
    permission_classes: ClassVar[list[type[permissions.BasePermission]]] = [permissions.IsAuthenticated]

    def get_instance(
        self,
        identifier: str,
    ) -> DttotDocReportCorporate:
        """To attempt retrieving a DTTOT Corporate Report document details for DTTOT Corporate Report ID.

        Args:
        ----
        identifier: The DTTOT Corporate Report ID to retrieve.

        Returns:
        -------
            The DTTOT Corporate Report document details for DTTOT Corporate Report ID.

        """
        try:
            instance = DttotDocReportCorporate.objects.get(
                dttotdoc_report=identifier,
            )
        except DttotDocReportCorporate.DoesNotExist:
            try:
                instance = DttotDocReportCorporate.objects.get(
                    dttotdoc_report_corporate_id=identifier,
                )
            except DttotDocReportCorporate.DoesNotExist:
                return None
        return instance

    @extend_schema(responses={200: DttotDocReportCorporateSerializer})
    def get(
        self,
        request: Any,
    ) -> Response:
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response(
                {"error": "The 'identifier' query parameter is required / invalid identifier"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        logger.info("Fetching DTTOT Corporate Report document details for DTTOT Corporate Report ID: %s", identifier)
        instance = self.get_instance(identifier)

        if instance is None:
            return Response(
                {"error": "No DTTOT Corporate Report document details found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = DttotDocReportCorporateSerializer(instance)
        logger.info("Successfully fetched DTTOT Corporate Report document details for identifier: %s", identifier)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=DttotDocReportCorporateSerializer,
        responses={200: DttotDocReportCorporateSerializer},
    )
    def put(
        self,
        request: Any,
    ) -> Response:
        """Update DTTOT Corporate Report document details for given identifier."""
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response(
                {"error": "The 'identifier' query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        logger.info("Updating DTTOT Corporate Report document details for given identifier: %s", identifier)
        instance = self.get_instance(identifier)
        if instance is None:
            return Response(
                {"error": "No DTTOT Corporate Report document details found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = DttotDocReportCorporateSerializer(
            instance,
            data=request.data,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=DttotDocReportCorporateSerializer,
        responses={200: DttotDocReportCorporateSerializer},
    )
    def patch(
        self,
        request: Any,
    ) -> Response:
        """To partially update DTTOT Corporate Report Document details for DTTOT Corporate Report ID."""
        identifier = request.query_params.get("identifier")
        logger.info("Partially updating DTTOT Corporate Report document details for given identifier: %s", identifier)

        if not identifier:
            return Response(
                {"error": "The 'identifier' query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Logging the partial update operation
        logger.info(
            "Partially updating DTTOT Corporate Report document details for given identifier: %s",
            identifier,
        )

        # Fetching the DTTOT Corporate Report document
        instance = self.get_instance(identifier)

        # Initializing the serializer with the fetched document and request data
        serializer = DttotDocReportCorporateSerializer(
            instance,
            data=request.data,
            partial=True,
        )
        # Checking if the serializer is valid
        if serializer.is_valid():
            # Saving the updated document
            serializer.save()

            # Logging the successful partial update operation
            logger.info(
                "Successfully partially updated DTTOT Corporate Report document details for given identifier: %s",
                identifier,
            )

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
        # Logging the failed partial update operation
        logger.error(
            "Failed to partially update DTTOT Corporate Report document details for given identifier: %s, errors: %s",
            identifier,
            serializer.errors,
        )

        # Returning the serializer errors in the response with a bad request status
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(
        self,
        request: Any,
    ) -> Response:
        """To delete DTTOT Corporate Report document details for DTTOT Corporate Report ID."""
        # Retrieve identifier from query params
        identifier = request.query_params.get("identifier")
        logger.info("Deleting DTTOT Corporate Report document details for given identifier: %s", identifier)

        # Checking if the identifier is provided
        if not identifier:
            return Response(
                {"error": "The 'identifier' query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetching the DTTOT Corporate Report document
        instance = self.get_instance(identifier)

        # Deleting the DTTOT Corporate Report document
        if instance is None:
            return Response(
                {"error": "No DTTOT Corporate Report document details found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        instance.delete()

        # Logging the successful delete operation
        logger.info(
            "Successfully deleted DTTOT Corporate Report document details for given identifier: %s",
            identifier,
        )

        # Returning the response with a no content status
        return Response(
            {"detail": "DTTOT Corporate Report document details deleted successfully"},
            status=status.HTTP_204_NO_CONTENT)
