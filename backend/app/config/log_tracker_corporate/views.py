from __future__ import annotations

from typing import Any, ClassVar

from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.common.routers import CustomViewRouter
from app.config.core.models import log_tracker_corporate
from app.config.log_tracker_corporate.serializers import (
    LogTrackerCorporateListSerializer,
    LogTrackerCorporateSerializer,
)

router = CustomViewRouter(url_prefix="api/")


@router.register_decorator(
    r"documents/log-tracker-corporate/list/",
    name="log-tracker-corporate-list",
)
class LogTrackerCorporateListView(generics.ListAPIView):
    serializer_class = LogTrackerCorporateListSerializer
    permission_classes: ClassVar = [permissions.IsAuthenticated]
    queryset = log_tracker_corporate.objects.all()

@router.register_decorator(
    r"documents/log-tracker-corporate/details/$",
    name="log-tracker-corporate-details",
)
class LogTrackerCorporateDetailView(APIView):
    serializer_class = LogTrackerCorporateSerializer
    permission_classes: ClassVar = [permissions.IsAuthenticated]

    def get_instance(self, identifier: str) -> log_tracker_corporate:
        """To attempt to retrieve a Log Tracker Corporate instance by either its document ID or its UUID.

        Args:
        ----
            identifier: The document ID or UUID of the Log Tracker Corporate instance to be retrieved.

        Returns:
        -------
            The retrieved Log Tracker Corporate instance, or None if no instance with the given identifier was found.

        """
        try:
            instance = log_tracker_corporate.objects.get(document=identifier)
        except log_tracker_corporate.DoesNotExist:
            try:
                instance = log_tracker_corporate.objects.get(log_tracker_corporate_id=identifier)
            except log_tracker_corporate.DoesNotExist:
                return None
        return instance

    @extend_schema(responses={200: LogTrackerCorporateSerializer})
    def get(
        self,
        request: Any,
        *_args: Any,
        **_kwargs: Any,
    ) -> Response:
        """To retrieve a Log Tracker Corporate instance by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the Log Tracker Corporate instance.

        **Example:**

        .. code-block:: http

            GET /api/log-tracker-corporate/details/123e4567-e89b-12d3-a456-426614174000 HTTP/1.1
            Host: example.org
            Accept: application/json

        .. code-block:: http

            HTTP/1.1 200 OK
            Content-Type: application/json
            Content-Length: 10

        **Responses:**

        .. code-block:: http

            {
                "log_tracker_corporate_id": "123e4567-e89b-12d3-a456-426614174000"
            }

        """
        identifier = request.query_params.get("identifier")
        instance = self.get_instance(identifier)
        if instance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = LogTrackerCorporateSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=LogTrackerCorporateSerializer,
        responses={200: LogTrackerCorporateSerializer},
    )
    def patch(
        self,
        request: Any,
        *_args: Any,
        **_kwargs: Any,
    ) -> Response:
        """To update a Log Tracker Corporate instance by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the Log Tracker Corporate instance.

        **Example:**

        .. code-block:: http

            PATCH /api/log-tracker-corporate/details/123e4567-e89b-12d3-a456-426614174000 HTTP/1.1
            Host: example.org
            Accept: application/json
            Content-Type: application/json

        .. code-block:: http

            {
                "log_tracker_corporate_id": "123e4567-e89b-12d3-a456-426614174000"
            }

        **Request Body:**

        * `LogTrackerCorporate` object with updated fields.

        **Responses:**

        .. code-block:: http

            HTTP/1.1 200 OK
            Content-Type: application/json
            Content-Length: 10

        """
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response(
                {"detail": "identifier query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance = self.get_instance(identifier)
        if instance is None:
            return Response(
                {"detail": "Log Tracker Corporate instance not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = LogTrackerCorporateSerializer(instance, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"detail": "Failed to update Log Tracker Corporate instance"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        request=LogTrackerCorporateSerializer,
        responses={200: LogTrackerCorporateSerializer},
    )
    def put(
        self,
        request: Any,
        *_args: Any,
        **_kwargs: Any,
    ) -> Response:
        """To create a new Log Tracker Corporate instance.

        **Query Parameters:**

        * `identifier`: The unique identifier of the Log Tracker Corporate instance.

        **Example:**

        .. code-block:: http

            PUT /api/log-tracker-corporate/details/123e4567-e89b-12d3-a456-426614174000 HTTP/1.1
            Host: example.org
            Accept: application/json
            Content-Type: application/json

        **Request Body:**

        .. code-block:: http

            PUT /api/log-tracker-corporate/details/123e4567-e89b-12d3-a456-426614174000 HTTP/1.1
            Host: example.org
            Accept: application/json
            Content-Type: application/json

        .. code-block:: http

            {
                "log_tracker_corporate_id": "123e4567-e89b-12d3-a456-426614174000"
            }

        **Responses:**

        .. code-block:: http

            HTTP/1.1 200 OK
            Content-Type: application/json
            Content-Length: 10

        """
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response(
                {"detail": "identifier query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance = self.get_instance(identifier)
        if instance is None:
            return Response(
                {"detail": "Log Tracker Corporate instance not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = LogTrackerCorporateSerializer(instance, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"detail": "Failed to update Log Tracker Corporate instance"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        responses={200: LogTrackerCorporateSerializer},
    )
    def delete(
        self,
        request: Any,
        *_args: Any,
        **_kwargs: Any,
    ) -> Response:
        """To delete a Log Tracker Corporate instance by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the Log Tracker Corporate instance.

        **Example:**

        .. code-block:: http

            DELETE /api/log-tracker-corporate/details/123e4567-e89b-12d3-a456-426614174000 HTTP/1.1
            Host: example.org
            Accept: application/json

        **Response:**

        .. code-block:: http

            HTTP/1.1 200 OK
            Content-Type: application/json
            Content-Length: 0

        """
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response(
                {"detail": "identifier query parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance = self.get_instance(identifier)
        if instance is None:
            return Response(
                {"detail": "Log Tracker Corporate instance not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        instance.delete()
        return Response(
            {"detail": "Log Tracker Corporate instance deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )
