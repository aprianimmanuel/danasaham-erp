from __future__ import annotations

import logging
from typing import Any, ClassVar

from drf_spectacular.utils import extend_schema  #type: ignore # noqa: PGH003
from rest_framework import generics, permissions, status  #type: ignore # noqa: PGH003
from rest_framework.generics import GenericAPIView  #type: ignore # noqa: PGH003
from rest_framework.response import Response  #type: ignore # noqa: PGH003

from app.common.routers import CustomViewRouter  #type: ignore # noqa: PGH003
from app.documents.dttotDoc.dttotDocReportPersonal.models import (  #type: ignore # noqa: PGH003
    DttotDocReportPersonal,
)
from app.documents.dttotDoc.dttotDocReportPersonal.serializers import (  #type: ignore # noqa: PGH003
    DttotDocReportPersonalSerializer,
)

logger = logging.getLogger(__name__)

router = CustomViewRouter(url_prefix="api/")

@router.register_decorator(
    r"documents/dttotdocreport/dttotReportPersonal/list/",
    name="dttot-report-personal-list",
)
class dttotDocReportPersonalView(generics.ListAPIView):  # noqa: N801
    serializer_class = DttotDocReportPersonalSerializer
    permission_classes: ClassVar[list[type[permissions.BasePermission]]] = [permissions.IsAuthenticated]
    queryset = DttotDocReportPersonal.objects.all()

@router.register_decorator(
    r"documents/dttotdocreport/dttotReportPersonal/details/$",
    name="dttot-report-personal-detail",
)
class dttotDocReportPersonalDetailView(GenericAPIView):  # noqa: N801
    serializer_class = DttotDocReportPersonalSerializer
    permission_classes: ClassVar[list[type[permissions.BasePermission]]] = [permissions.IsAuthenticated]

    def get_instance(
            self,
            identifier: str,
    ) -> DttotDocReportPersonal:
        """To attempt retrieving a DTTOT Personal Report document details for DTTOT Personal Report ID.

        Args:
        ----
            identifier: The DTTOT Personal Report ID to retrieve.

        Returns:
        -------
            The DTTOT Personal Report document details for DTTOT Personal Report ID.

        """
        try:
            instance = DttotDocReportPersonal.objects.get(
                dttotdoc_report=identifier,
            )
        except DttotDocReportPersonal.DoesNotExist:
            try:
                instance = DttotDocReportPersonal.objects.get(
                    dttotdoc_report_personal_id=identifier,
                )
            except DttotDocReportPersonal.DoesNotExist:
                return None
        return instance

    @extend_schema(responses={200: DttotDocReportPersonalSerializer})
    def get(
        self,
        request: Any) -> Response:
        # Retrieve identifier from query params
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response(
                {
                    "detail": "Identifier query parameter is required / invalid identifier",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        logger.info("Fetching DTTOT Personal Report document details for identifier: %s", identifier)

        instance = self.get_instance(identifier)

        if instance is None:
            return Response(
                {"detail": "No DTTOT Personal Report document found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = DttotDocReportPersonalSerializer(instance)
        logger.info("Successfully fetched DTTOT Personal Report document details for identifier: %s", identifier)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=DttotDocReportPersonalSerializer,
        responses={200: DttotDocReportPersonalSerializer},
    )
    def put(self, _request: Any) -> Response:
        """Update DTTOT Personal Report document for DTTOT Personal Report document ID.

        Args:
        ----
            _request: Request object.

        Returns:
        -------
            Response: Response object.

        """
        # Retrieve identifier from query params
        identifier = _request.query_params.get("identifier")
        if not identifier:
            return Response({"detail": "Identifier query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Logging the update operation
        logger.info(
            "Updating DTTOT Personal Report document for given identifier: %s",
            identifier,
        )

        # Fetching the DTTOT Personal Report document
        instance = self.get_instance(identifier)

        # Initializing the serializer with the fetched document and request data
        serializer = DttotDocReportPersonalSerializer(
            instance,
            data=_request.data,
        )

        # Checking if the serializer is valid
        if serializer.is_valid():
            # Saving the updated document
            serializer.save()

            # Logging the successful update operation
            logger.info(
                "Successfully updated DTTOT Personal Report document given identifier: %s",
                identifier,
            )

            # Returning the updated document data in the response
            return Response(serializer.data, {"detail": "Updated successfully."})

        # Logging the failed update operation
        logger.error(
            "Failed to update DTTOT Personal Report document for given identifier: %s, errors: %s",
            identifier,
            serializer.errors,
        )

        # Returning the serializer errors in the response with a bad request status
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST, data={"detail": "Failed to update."})

    @extend_schema(
        request=DttotDocReportPersonalSerializer,
        responses={200: DttotDocReportPersonalSerializer},
    )
    def patch(self, _request: Any) -> Response:
        """To partially update DTTOT Personal Report document for given identifier.

        Args:
        ----
            _request: Request object.

        Returns:
        -------
            Response: Response object.

        """
        # Retrieve identifier from query params
        identifier = _request.query_params.get("identifier")
        if not identifier:
            return Response({"detail": "Identifier query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Logging the partial update operation
        logger.info(
            "Partially updating DTTOT Personal Report document for given identifier: %s",
            identifier,
        )

        # Fetching the DTTOT Personal Report document
        instance = self.get_instance(identifier)

        # Initializing the serializer with the fetched document and request data
        serializer = DttotDocReportPersonalSerializer(
            instance,
            data=_request.data,
            partial=True,
        )

        # Checking if the serializer is valid
        if serializer.is_valid():
            # Saving the updated document
            serializer.save()

            # Logging the successful partial update operation
            logger.info(
                "Successfully partially updated DTTOT Personal Report document for given identifier: %s",
                identifier,
            )

            # Returning the updated document data in the response
            return Response(serializer.data, {"detail": "Partially updated successfully."})

        # Logging the failed partial update operation
        logger.error(
            "Failed to partially update DTTOT Personal Report document for DTTOT ID: %s, errors: %s",
            identifier,
            serializer.errors,
        )

        # Returning the serializer errors in the response with a bad request status
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST, data={"detail": "Failed to partially update."})

    @extend_schema(responses={204: None})
    def delete(self, _request: Any) -> Response:
        """Delete DTTOT Personal Report document for DTTOT Personal Report document ID.

        Args:
        ----
            _request: Request object.

        Returns:
        -------
            Response: Response object.

        """
        # Retrieve identifier from query params
        identifier = _request.query_params.get("identifier")
        if not identifier:
            return Response({"detail": "Identifier query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Logging the delete operation
        logger.info("Deleting DTTOT Personal Report document for DTTOT Personal Report document ID: %s", identifier)

        # Fetching the DTTOT Personal Report document
        instance = self.get_instance(identifier)

        # Deleting the DTTOT Personal Report document
        instance.delete()

        # Logging the successful delete operation
        logger.info("Successfully deleted DTTOT Personal Report document for DTTOT ID: %s", identifier)

        # Returning a no content response
        return Response(
            {"detail": "DTTOT Personal Report document deleted successfully"},
            status=status.HTTP_204_NO_CONTENT)


