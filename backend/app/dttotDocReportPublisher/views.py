from __future__ import annotations

import logging
from typing import Any, ClassVar

from drf_spectacular.utils import extend_schema  #type: ignore # noqa: PGH003
from rest_framework import generics, permissions, status  #type: ignore # noqa: PGH003
from rest_framework.generics import GenericAPIView  #type: ignore # noqa: PGH003
from rest_framework.response import Response  #type: ignore # noqa: PGH003

from app.common.routers import CustomViewRouter  #type: ignore # noqa: PGH003
from app.dttotDocReportPublisher.models import (  #type: ignore # noqa: PGH003
    dttotDocReportPublisher,
)
from app.dttotDocReportPublisher.serializers import (  #type: ignore # noqa: PGH003
    DttotDocReportPublisherSerializer,
)

logger = logging.getLogger(__name__)

router = CustomViewRouter(url_prefix="api/")

@router.register_decorator(
    r"documents/dttotdocreport/dttotReportPublisher/list/",
    name="dttot-report-publisher-list",
)
class dttotDocReportPublisherView(generics.ListAPIView):  # noqa: N801
    serializer_class = DttotDocReportPublisherSerializer
    permission_classes: ClassVar[list[type[permissions.BasePermission]]] = [permissions.IsAuthenticated]
    queryset = dttotDocReportPublisher.objects.all()

@router.register_decorator(
    r"documents/dttotdocreport/dttotReportPublisher/details/$",
    name="dttot-report-publisher-detail",
)
class dttotDocReportPublisherDetailView(GenericAPIView):  # noqa: N801
    serializer_class = DttotDocReportPublisherSerializer
    permission_classes: ClassVar[list[type[permissions.BasePermission]]] = [permissions.IsAuthenticated]

    def get_instance(
        self,
        identifier: str,
    ) -> dttotDocReportPublisher:
        """To attempt retrieving a DTTOT Publisher Report document details for DTTOT Publisher Report ID.

        Args:
        ----
        identifier: The DTTOT Publisher Report ID to retrieve.

        Returns:
        -------
            The DTTOT Publisher Report document details for DTTOT Publisher Report ID.

        """
        try:
            instance = dttotDocReportPublisher.objects.get(
                dttotdoc_report=identifier,
            )
        except dttotDocReportPublisher.DoesNotExist:
            try:
                instance = dttotDocReportPublisher.objects.get(
                    dttotdoc_report_publisher_id=identifier,
                )
            except dttotDocReportPublisher.DoesNotExist:
                return None
        return instance

    @extend_schema(responses={200: DttotDocReportPublisherSerializer})
    def get(
        self,
        request: Any,
    ) -> Response:
        identifier = request.query_params.get("identifier")
        logger.info("Fetching DTTOT Publisher Report document details for given identifier: %s", identifier)
        if not identifier:
            return Response(
                {"error": "identifier is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance = self.get_instance(identifier)

        if instance is None:
            return Response(
                {"error": "No DTTOT Publisher Report document details found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = DttotDocReportPublisherSerializer(instance)
        logger.info("Successfully fetched DTTOT Publisher Report document details for given identifier: %s", identifier)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=DttotDocReportPublisherSerializer,
        responses={200: DttotDocReportPublisherSerializer},
    )
    def put(
        self,
        request: Any,
    ) -> Response:
        """Update DTTOT Publisher Report document details for DTTOT Publisher Report ID.

        Args:
        ----
            request: Request object.

        Returns:
        -------
            Response object.

        """
        # Retrieving identifier from query params
        identifier = request.query_params.get("identifier")

        # Checking if the identifier is provided
        if not identifier:
            return Response(
                {"error": "The 'identifier' query parameter is required / invalid identifier"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Logging the update operation
        logger.info(
            "Updating DTTOT Publisher Report document details for given identifier: %s",
            identifier,
        )

        # Fetching the DTTOT Publisher Report document
        instance = self.get_instance(identifier)

        # Checking if the DTTOT Publisher Report document exists
        if instance is None:
            return Response(
                {"error": "No DTTOT Publisher Report document details found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Initializing the serializer with the fetched document and request data
        serializer = DttotDocReportPublisherSerializer(
            instance,
            data=request.data,
        )

        # Checking if the serializer is valid
        if serializer.is_valid():
            # Saving the updated document
            serializer.save()
            logger.info(
                "Successfully updated DTTOT document details for given identifier: %s",
                identifier,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Logging the failed update operation
        logger.info(
            "Failed to update DTTOT document details for DTTOT ID: %s",
            identifier,
        )
        return Response(serializer.errors, {"detail": "Failed to update DTTOT Publisher Report document details."}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=DttotDocReportPublisherSerializer,
        responses={200: DttotDocReportPublisherSerializer},
    )
    def patch(
        self,
        request: Any,
    ) -> Response:
        """To partially update DTTOT Publisher Report document details for given identifier.

        Args:
        ----
            request: Request object.

        Returns:
        -------
            Response object.

        """
        # Retrieving identifier from query params
        identifier = request.query_params.get("identifier")

        # Logging the update operation
        logger.info(
            "Partially updating DTTOT Publisher Report document details for given identifier: %s",
            identifier,
        )

        # Checking if the identifier is provided
        if not identifier:
            return Response(
                {"error": "The 'identifier' query parameter is required / invalid identifier"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Logging the partial update operation
        logger.info(
            "Partially updating DTTOT Publisher Report document details for given identifier: %s",
            identifier,
        )

        # Fetching the DTTOT Publisher Report document
        instance = self.get_instance(identifier)

        # Checking if the DTTOT Publisher Report document exists
        if instance is None:
            return Response(
                {"error": "No DTTOT Publisher Report document details found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Initializing the serializer with the fetched document and request data
        serializer = DttotDocReportPublisherSerializer(
            instance,
            data=request.data,
            partial=True,
        )

        # Checking if the serializer is valid
        if serializer.is_valid():
            # Saving the updated document
            serializer.save()
            logger.info(
                "Successfully partially updated DTTOT Report document details for given identifier: %s",
                instance,
            )
            return Response(
                serializer.data,
                status=status.HTTP_200_OK)

        # Logging the failed partial update operation
        logger.info(
            "Failed to partially update DTTOT document details for given identifier: %s",
            identifier,
        )
        # Returning the error response
        return Response(
            {"detail": "Failed to partially update DTTOT Publisher Report document details."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(responses={204: None})
    def delete(
        self,
        request: Any,
    ) -> Response:
        """Delete DTTOT Publisher Report document details for given identifier.

        Args:
        ----
            request: Request object.

        Returns:
        -------
            Response object.

        """
        # Retrieve identifier from query params
        identifier = request.query_params.get("identifier")

        # Logging the delete operation
        logger.info(
            "Deleting DTTOT Publisher Report document details for given identifier: %s",
            identifier,
        )

        # Checking if the identifier is provided
        if not identifier:
            return Response(
                {"error": "The 'identifier' query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetching the DTTOT Publisher Report document
        instance = self.get_instance(identifier)

        if instance is None:
            return Response(
                {"error": "No DTTOT Publisher Report document details found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Deleting the DTTOT Publisher Report document
        instance.delete()

        # Logging the successful delete operation
        logger.info(
            "Successfully deleted DTTOT document details for given identifier: %s",
            identifier,
        )

        # Returning a 204 status code
        return Response(
            {"detail": "Successfully deleted DTTOT Publisher Report document details."},
            status=status.HTTP_204_NO_CONTENT,
        )
