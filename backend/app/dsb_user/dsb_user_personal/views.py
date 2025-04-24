from __future__ import annotations

from typing import Any, ClassVar

from drf_spectacular.utils import extend_schema  #type: ignore  # noqa: PGH003
from rest_framework import generics, permissions, status  #type: ignore  # noqa: PGH003
from rest_framework.response import Response  #type: ignore  # noqa: PGH003
from rest_framework.views import APIView  #type: ignore  # noqa: PGH003

from app.common.routers import CustomViewRouter  #type: ignore  # noqa: PGH003
from app.dsb_user.dsb_user_personal.models import (  #type: ignore  # noqa: PGH003
    DsbUserPersonal,
)
from app.dsb_user.dsb_user_personal.serializers import (  #type: ignore  # noqa: PGH003
    DsbUserPersonalListSerializer,
    DsbUserPersonalSerializer,
)

router = CustomViewRouter(url_prefix="api/")


@router.register_decorator(r"dsb-user-personal/list/", name="dsb-user-personal-list")
class DsbUserPersonalListView(generics.ListAPIView):
    serializer_class = DsbUserPersonalListSerializer
    permission_classes: ClassVar = [permissions.IsAuthenticated]
    queryset = DsbUserPersonal.objects.all()


@router.register_decorator(
    r"dsb-user-personal/details/$",
    name="dsb-user-personal-details",
)
class DsbUserPersonalDetailView(APIView):
    permission_classes: ClassVar = [permissions.IsAuthenticated]

    def get_instance(self, identifier: str) -> DsbUserPersonal:
        """To attempt to retrieve a DSB user personal data by either its document ID or its UUID.

        Args:
        ----
            identifier: The document ID or UUID of the DSB user personal data to be retrieved.

        Returns:
        -------
            The retrieved DSB user personal data, or None if no data with the given identifier was found.

        """
        try:
            instance = DsbUserPersonal.objects.get(document=identifier)
        except DsbUserPersonal.DoesNotExist:
            try:
                instance = DsbUserPersonal.objects.get(dsb_user_personal_id=identifier)
            except DsbUserPersonal.DoesNotExist:
                return None
        return instance

    @extend_schema(responses={200: DsbUserPersonalSerializer})
    def get(self, request: Any, *_args: Any, **_kwargs: Any) -> Response:
        """To retrieve a DSB user personal data by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the DSB user personal data to be retrieved.

        **Responses:**

        * `200 OK`: Returns the DSB user personal data with the given ID.
        * `400 Bad Request`: The `identifier` query parameter is required.
        * `404 Not Found`: No DSB user personal data with the given ID was found.

        **Security:**

        * `jwtAuth`, `tokenAuth`, `jwtHeaderAuth`, `jwtCookieAuth`: The request is authenticated using a JSON Web Token.
        """
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response({"detail": "Identifier query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_instance(identifier)
        if instance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DsbUserPersonalSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=DsbUserPersonalSerializer, responses={200: DsbUserPersonalSerializer})
    def put(self, request: Any, *_args: Any, **_kwargs: Any) -> Response:
        """To update a DSB User Personal instance by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the DSB User Personal instance.

        **Request Body:**

        * `DsbUserPersonal` object with updated fields.

        **Responses:**

        * `200 OK`: Returns the updated DSB User Personal instance.
        * `400 Bad Request`: The `identifier` query parameter is required.
        * `404 Not Found`: No DSB User Personal instance with the given ID was found.

        **Security:**

        * `jwtAuth`, `tokenAuth`, `jwtHeaderAuth`, `jwtCookieAuth`: The request is authenticated using a JSON Web Token.
        """
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response({"detail": "Identifier query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_instance(identifier)
        if instance is None:
            return Response(
                {"detail": "No DSB User Personal instance with the given ID was found."},
                status=status.HTTP_404_NOT_FOUND)

        serializer = DsbUserPersonalSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=DsbUserPersonalSerializer, responses={200: DsbUserPersonalSerializer})
    def patch(self, request: Any, *_args: Any, **_kwargs: Any) -> Response:
        """To partially update a DSB User Personal instance by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the DSB User Personal instance.

        **Request Body:**

        * `DsbUserPersonal` object with updated fields.

        **Responses:**

        * `200 OK`: Returns the updated DSB User Personal instance.
        * `400 Bad Request`: The `identifier` query parameter is required.
        * `404 Not Found`: No DSB User Personal instance with the given ID was found.

        **Security:**

        * `jwtAuth`, `tokenAuth`, `jwtHeaderAuth`, `jwtCookieAuth`: The request is authenticated using a JSON Web Token.
        """
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response({"detail": "Identifier query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_instance(identifier)
        if instance is None:
            return Response(
                {"detail": "No DSB User Personal instance with the given ID was found."},
                status=status.HTTP_404_NOT_FOUND)

        serializer = DsbUserPersonalSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses={204: None})
    def delete(self, request: Any, *_args: Any, **_kwargs: Any) -> Response:
        """To delete a DSB User Personal instance by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the DSB User Personal instance.

        **Responses:**

        * `204 No Content`: DSB User Personal instance successfully deleted, no response body.
        * `400 Bad Request`: The `identifier` query parameter is required.
        * `404 Not Found`: No DSB User Personal instance with the given ID was found.

        **Security:**

        * `jwtAuth`, `tokenAuth`, `jwtHeaderAuth`, `jwtCookieAuth`: The request is authenticated using a JSON Web Token.
        """
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response({"detail": "Identifier query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_instance(identifier)
        if instance is None:
            return Response(
                {"detail": "No DSB User Personal instance with the given ID was found."},
                status=status.HTTP_404_NOT_FOUND)

        instance.delete()
        return Response(
            {"detail": "DSB User Personal instance has been successfully deleted!"},
            status=status.HTTP_204_NO_CONTENT)
