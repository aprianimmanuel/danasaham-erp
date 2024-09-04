from __future__ import annotations

from typing import Any, ClassVar

from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.common.routers import CustomViewRouter
from app.config.core.models import log_tracker_personal
from app.config.log_tracker_personal.serializers import (
    LogTrackerPersonalListSerializer,
    LogTrackerPersonalSerializer,
)

router = CustomViewRouter(url_prefix="api/")


@router.register_decorator(
    r"documents/log-tracker-personal/list/",
    name="log-tracker-personal-list",
)
class LogTrackerPersonalListView(generics.ListAPIView):
    serializer_class = LogTrackerPersonalListSerializer
    permission_classes: ClassVar = [permissions.IsAuthenticated]
    queryset = log_tracker_personal.objects.all()


@router.register_decorator(
    r"documents/log-tracker-personal/details/$",
    name="log-tracker-personal-details",
)
class LogTrackerPersonalDetailView(APIView):
    serializer_class = LogTrackerPersonalSerializer
    permission_classes: ClassVar = [permissions.IsAuthenticated]

    def get_instance(self, identifier: str) -> log_tracker_personal:
        """To attempt to retrieve a Log Tracker Personal instance by either its document ID or its UUID.

        Args:
        ----
            identifier: The document ID or UUID of the Log Tracker Personal instance to be retrieved.

        Returns:
        -------
            The retrieved Log Tracker Personal instance, or None if no instance with the given identifier was found.

        """
        try:
            instance = log_tracker_personal.objects.get(document=identifier)
        except log_tracker_personal.DoesNotExist:
            try:
                instance = log_tracker_personal.objects.get(log_tracker_personal_id=identifier)
            except log_tracker_personal.DoesNotExist:
                return None
        return instance

    @extend_schema(responses={200: LogTrackerPersonalSerializer})
    def get(self, request: Any, *_args: Any, **_kwargs: Any) -> Response:
        """To retrieve a Log Tracker Personal instance by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the Log Tracker Personal instance.

        **Example:**

        .. code-block:: http

            GET /api/log-tracker-personal/details/123e4567-e89b-12d3-a456-426614174000 HTTP/1.1
            Host: example.org
            Accept: application/json

        .. code-block:: http

            HTTP/1.1 200 OK
            Content-Type: application/json
            Content-Length: 10

        **Response:**

        .. code-block:: http

            {
                "log_tracker_personal_id": "123e4567-e89b-12d3-a456-426614174000"
            }

        """
        identifier = request.query_params.get("identifier")
        instance = self.get_instance(identifier)
        if instance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=LogTrackerPersonalSerializer, responses={200: LogTrackerPersonalSerializer})
    def put(self, request: Any, *_args: Any, **_kwargs: Any) -> Response:
        """To update a Log Tracker Personal instance by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the Log Tracker Personal instance.

        **Request Body:**

        * `LogTrackerPersonal` object with updated fields.

        **Example:**

        .. code-block:: http

            PUT /api/log-tracker-personal/details/123e4567-e89b-12d3-a456-426614174000 HTTP/1.1
            Host: example.org
            Accept: application/json

        .. code-block:: http

            {
                "log_tracker_personal_id": "123e4567-e89b-12d3-a456-426614174000"
            }

        **Response:**

        .. code-block:: http

            HTTP/1.1 200 OK
            Content-Type: application/json
            Content-Length: 10

        """
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response(
                {"detail": "Missing 'identifier' query parameter"},
                status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_instance(identifier)
        if instance is None:
            return Response(
                {"detail": "Log Tracker Personal instance not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = LogTrackerPersonalSerializer(instance, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"detail": "Invalid request body"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
            request=LogTrackerPersonalSerializer,
            responses={200: LogTrackerPersonalSerializer},
        )
    def patch(
        self,
        request: Any,
        *_args: Any,
        **_kwargs: Any,
    ) -> Response:
        """To partially update a Log Tracker Personal instance by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the Log Tracker Personal instance.

        **Request Body:**
        * `LogTrackerPersonal` object with updated fields.

        **Example:**

        .. code-block:: http

            PATCH /api/log-tracker-personal/details/123e4567-e89b-12d3-a456-426614174000 HTTP/1.1
            Host: example.org
            Accept: application/json

        .. code-block:: http

            {
                "log_tracker_personal_id": "123e4567-e89b-12d3-a456-426614174000"
            }

        **Response:**

        .. code-block:: http

            HTTP/1.1 200 OK
            Content-Type: application/json
            Content-Length: 10

        """
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response(
                {"detail": "Missing 'identifier' query parameter"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance = self.get_instance(identifier)
        if instance is None:
            return Response(
                {"detail": "Log Tracker Personal instance not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = LogTrackerPersonalSerializer(instance, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"detail": "Invalid request body"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(responses={200: LogTrackerPersonalSerializer})
    def delete(
        self,
        request: Any,
        *_args: Any,
        **_kwargs: Any,
    ) -> Response:
        """To delete a Log Tracker Personal instance by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the Log Tracker Personal instance.

        **Example:**

        .. code-block:: http

            DELETE /api/log-tracker-personal/details/123e4567-e89b-12d3-a456-426614174000 HTTP/1.1
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
                {"detail": "Missing 'identifier' query parameter"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance = self.get_instance(identifier)
        if instance is None:
            return Response(
                {"detail": "Log Tracker Personal instance not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        instance.delete()
        return Response(
            {"detail": "Log Tracker Personal instance deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )
