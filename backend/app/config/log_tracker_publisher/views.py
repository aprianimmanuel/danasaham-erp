from __future__ import annotations

from typing import Any, ClassVar

from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.common.routers import CustomViewRouter
from app.config.core.models import log_tracker_publisher
from app.config.log_tracker_publisher.serializers import (
    LogTrackerPublisherListSerializer,
    LogTrackerPublisherSerializer,
)

router = CustomViewRouter(url_prefix="api/")


@router.register_decorator(
    r"documents/log-tracker-publisher/list/",
    name="log-tracker-publisher-list",
)
class LogTrackerPublisherListView(generics.ListAPIView):
    serializer_class = LogTrackerPublisherListSerializer
    permission_classes: ClassVar = [permissions.IsAuthenticated]
    queryset = log_tracker_publisher.objects.all()


@router.register_decorator(
    r"documents/log-tracker-publisher/details/$",
    name="log-tracker-publisher-details",
)
class LogTrackerPublisherDetailView(APIView):
    serializer_class = LogTrackerPublisherSerializer
    permission_classes: ClassVar = [permissions.IsAuthenticated]

    def get_instance(self, identifier: str) -> log_tracker_publisher:
        """To attempt to retrieve a Log Tracker Publisher instance by either its document ID or its UUID.

        Args:
        ----
            identifier: The document ID or UUID of the Log Tracker Publisher instance to be retrieved.

        Returns:
        -------
            The retrieved Log Tracker Publisher instance, or None if no instance with the given identifier was found.

        """
        try:
            instance = log_tracker_publisher.objects.get(document=identifier)
        except log_tracker_publisher.DoesNotExist:
            try:
                instance = log_tracker_publisher.objects.get(log_tracker_publisher_id=identifier)
            except log_tracker_publisher.DoesNotExist:
                return None
        return instance

    @extend_schema(responses={200: LogTrackerPublisherSerializer})
    def get(self, request: Any, *_args: Any, **_kwargs: Any) -> Response:
        """To retrieve a Log Tracker Publisher instance by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the Log Tracker Publisher instance.

        **Example:**

        .. code-block:: http

            GET /api/log-tracker-publisher/details/123e4567-e89b-12d3-a456-426614174000 HTTP/1.1
            Host: example.org
            Accept: application/json

        .. code-block:: http

            HTTP/1.1 200 OK
            Content-Type: application/json
            Content-Length: 0

        **Response:**

        .. code-block:: http

            {
                "log_tracker_publisher_id": "123e4567-e89b-12d3-a456-426614174000"
            }

        """
        identifier = request.query_params.get("identifier")
        instance = self.get_instance(identifier)
        if instance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = LogTrackerPublisherSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=LogTrackerPublisherSerializer, responses={200: LogTrackerPublisherSerializer})
    def put(self, request: Any, *_args: Any, **_kwargs: Any) -> Response:
        """To update a Log Tracker Publisher instance by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the Log Tracker Publisher instance.

        **Request Body:**

        * `LogTrackerPublisher` object with updated fields.

        **Example:**

        .. code-block:: http

            PUT /api/log-tracker-publisher/details/123e4567-e89b-12d3-a456-426614174000 HTTP/1.1
            Host: example.org
            Accept: application/json

        .. code-block:: http

            {
                "log_tracker_publisher_id": "123e4567-e89b-12d3-a456-426614174000"
            }

        **Response:**

        .. code-block:: http

            HTTP/1.1 200 OK
            Content-Type: application/json
            Content-Length: 0

        """
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response({"detail": "Identifier query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_instance(identifier)
        if instance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = LogTrackerPublisherSerializer(instance, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=LogTrackerPublisherSerializer,
        responses={200: LogTrackerPublisherSerializer},
    )
    def patch(
        self,
        request: Any,
        *_args: Any,
        **_kwargs: Any,
    ) -> Response:
        """To partially update a Log Tracker Publisher instance by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the Log Tracker Publisher instance.

        **Request Body:**

        * `LogTrackerPublisher` object with partial updated fields.

        **Example:**

        .. code-block:: http

            PATCH /api/log-tracker-publisher/details/123e4567-e89b-12d3-a456-426614174000 HTTP/1.1
            Host: example.org
            Accept: application/json

        .. code-block:: http

            {
                "log_tracker_publisher_id": "123e4567-e89b-12d3-a456-426614174000"
            }

        **Response:**

        .. code-block:: http

            HTTP/1.1 200 OK
            Content-Type: application/json
            Content-Length: 0

        """
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response({"detail": "Identifier query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_instance(identifier)
        if instance is None:
            return Response(
                {"detail": "No Log Tracker Publisher instance with the given ID was found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = LogTrackerPublisherSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={204: None},
    )
    def delete(
        self,
        request: Any,
        *_args: Any,
        **_kwargs: Any,
    ) -> Response:
        """To delete a Log Tracker Publisher instance by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the Log Tracker Publisher instance.

        **Example:**

        .. code-block:: http

            DELETE /api/log-tracker-publisher/details/123e4567-e89b-12d3-a456-426614174000 HTTP/1.1
            Host: example.org
            Accept: application/json

        **Response:**

        .. code-block:: http

            HTTP/1.1 204 No Content
            Content-Type: application/json
            Content-Length: 0

        """
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response({"detail": "Identifier query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_instance(identifier)
        if instance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
