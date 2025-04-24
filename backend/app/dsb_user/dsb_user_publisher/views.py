from __future__ import annotations

from typing import Any, ClassVar

from drf_spectacular.utils import extend_schema  #type: ignore # noqa: PGH003
from rest_framework import generics, permissions, status  #type: ignore # noqa: PGH003
from rest_framework.response import Response  #type: ignore # noqa: PGH003
from rest_framework.views import APIView  #type: ignore # noqa: PGH003

from app.common.routers import CustomViewRouter  #type: ignore # noqa: PGH003
from app.dsb_user.dsb_user_publisher.models import (  #type: ignore # noqa: PGH003
    DsbUserPublisher,
)
from app.dsb_user.dsb_user_publisher.serializers import (  #type: ignore # noqa: PGH003
    DsbUserPublisherSerializer,
)

router = CustomViewRouter(url_prefix="api/")


@router.register_decorator(r"dsb-user-publisher/list/", name="dsb-user-publisher-list")
class DsbUserPublisherListView(generics.ListAPIView):
    serializer_class = DsbUserPublisherSerializer
    permission_classes: ClassVar = [permissions.IsAuthenticated]
    queryset = DsbUserPublisher.objects.all()


@router.register_decorator(
    r"dsb-user-publisher/details/$",
    name="dsb-user-publisher-details",
)
class DsbUserPublisherDetailView(APIView):
    serializer_class = DsbUserPublisherSerializer
    permission_classes: ClassVar = [permissions.IsAuthenticated]

    def get_instance(self, identifier: str) -> DsbUserPublisher:
        """To attempt to retrieve a DSB User Publisher instance by either its document ID or its UUID.

        Args:
        ----
            identifier: The document ID or UUID of the DSB User Publisher instance to be retrieved.

        Returns:
        -------
            The retrieved DSB User Publisher instance, or None if no instance with the given identifier was found.

        """
        try:
            instance = DsbUserPublisher.objects.get(document=identifier)
        except DsbUserPublisher.DoesNotExist:
            try:
                instance = DsbUserPublisher.objects.get(dsb_user_publisher_id=identifier)
            except DsbUserPublisher.DoesNotExist:
                return None
        return instance

    @extend_schema(responses={200: DsbUserPublisherSerializer})
    def get(self, request: Any, *_args: Any, **_kwargs: Any) -> Response:
        """To retrieve a DSB User Publisher instance by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the DSB User Publisher instance.

        **Responses:**

        * `200 OK`: Returns the DSB User Publisher instance.
        * `400 Bad Request`: The `identifier` query parameter is required.
        * `404 Not Found`: No DSB User Publisher instance with the given ID was found.

        **Security:**

        * `jwtAuth`, `tokenAuth`, `jwtHeaderAuth`, `jwtCookieAuth`: The request is authenticated using a JSON Web Token.
        """
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response({"detail": "Identifier query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_instance(identifier)
        if instance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DsbUserPublisherSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=DsbUserPublisherSerializer, responses={200: DsbUserPublisherSerializer})
    def put(self, request: Any, *_args: Any, **_kwargs: Any) -> Response:
        """To update a DSB User Publisher instance by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the DSB User Publisher instance.

        **Request Body:**

        * `DsbUserPublisher` object with updated fields.

        **Responses:**

        * `200 OK`: Returns the updated DSB User Publisher instance.
        * `400 Bad Request`: The `identifier` query parameter is required.
        * `404 Not Found`: No DSB User Publisher instance with the given ID was found.

        **Security:**

        * `jwtAuth`, `tokenAuth`, `jwtHeaderAuth`, `jwtCookieAuth`: The request is authenticated using a JSON Web Token.
        """
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response({"detail": "Identifier query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_instance(identifier)
        if instance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = DsbUserPublisherSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=DsbUserPublisherSerializer, responses={200: DsbUserPublisherSerializer})
    def patch(self, request: Any, *_args: Any, **_kwargs: Any) -> Response:
        """To partially update a DSB User Publisher instance by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the DSB User Publisher instance.

        **Request Body:**

        * `DsbUserPublisher` object with updated fields.

        **Responses:**

        * `200 OK`: Returns the updated DSB User Publisher instance.
        * `400 Bad Request`: The `identifier` query parameter is required.
        * `404 Not Found`: No DSB User Publisher instance with the given ID was found.

        **Security:**

        * `jwtAuth`, `tokenAuth`, `jwtHeaderAuth`, `jwtCookieAuth`: The request is authenticated using a JSON Web Token.
        """
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response({"detail": "Identifier query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_instance(identifier)
        if instance is None:
            return Response(
                {"detail": "No DSB User Publisher instance with the given ID was found."},
                status=status.HTTP_404_NOT_FOUND)

        serializer = DsbUserPublisherSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses={204: None})
    def delete(self, request: Any, *_args: Any, **_kwargs: Any) -> Response:
        """To delete a DSB User Publisher instance by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the DSB User Publisher instance.

        **Responses:**

        * `204 No Content`: DSB User Publisher instance successfully deleted, no response body.
        * `400 Bad Request`: The `identifier` query parameter is required.
        * `404 Not Found`: No DSB User Publisher instance with the given ID was found.

        **Security:**

        * `jwtAuth`, `tokenAuth`, `jwtHeaderAuth`, `jwtCookieAuth`: The request is authenticated using a JSON Web Token.
        """
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response({"detail": "Identifier query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_instance(identifier)
        if instance is None:
            return Response(
                {"detail": "No DSB User Publisher instance with the given ID was found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        instance.delete()
        return Response(
            {"detail": "DSB User Publisher instance has been successfully deleted!"},
            status=status.HTTP_204_NO_CONTENT,
        )
