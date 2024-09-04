from __future__ import annotations

from typing import Any, ClassVar

from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.common.routers import CustomViewRouter
from app.config.core.models import dsb_user_corporate
from app.config.dsb_user_corporate.serializers import (
    DsbUserCorporateListSerializer,
    DsbUserCorporateSerializer,
)

router = CustomViewRouter(url_prefix="api/")


@router.register_decorator(r"documents/dsb-user-corporate/list/", name="dsb-user-corporate-list")
class DsbUserCorporateListView(generics.ListAPIView):
    serializer_class = DsbUserCorporateListSerializer
    permission_classes: ClassVar[list[type[permissions.BasePermission]]] = [permissions.IsAuthenticated]
    queryset = dsb_user_corporate.objects.all()


@router.register_decorator(
    r"documents/dsb-user-corporate/details/$",
    name="dsb-user-corporate-details",
)
class DsbUserCorporateDetailView(APIView):
    permission_classes: ClassVar = [permissions.IsAuthenticated]

    def get_instance(self, identifier: str) -> dsb_user_corporate:
        """To get a DSB User Corporate instance by identifier.

        The identifier can be either the document ID or the dsb_user_corporate_id.

        Args:
        ----
            identifier (str): The identifier of the DSB User Corporate instance.

        Returns:
        -------
            dsb_user_corporate: The DSB User Corporate instance, or None if it does not exist.

        """
        try:
            instance = dsb_user_corporate.objects.get(document=identifier)
        except dsb_user_corporate.DoesNotExist:
            try:
                instance = dsb_user_corporate.objects.get(dsb_user_corporate_id=identifier)
            except dsb_user_corporate.DoesNotExist:
                return None
        return instance

    @extend_schema(responses={200: DsbUserCorporateSerializer})
    def get(self, request: Any, *_args: Any, **_kwargs: Any) -> Response:
        """To retrieve a DSB User Corporate instance by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the DSB User Corporate instance.

        **Responses:**

        * `200 OK`: Returns the DSB User Corporate instance.
        * `400 Bad Request`: The `identifier` query parameter is required.
        * `404 Not Found`: No DSB User Corporate instance with the given ID was found.

        **Security:**

        * `jwtAuth`, `tokenAuth`, `jwtHeaderAuth`, `jwtCookieAuth`: The request is authenticated using a JSON Web Token.
        """
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response(
                {"detail": "Identifier query parameter is required / invalid identifier."},
                status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_instance(identifier)
        if instance is None:
            return Response(
                {"detail": "No DSB User Corporate instance with the given ID was found."},
                status=status.HTTP_404_NOT_FOUND)
        serializer = DsbUserCorporateSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=DsbUserCorporateSerializer, responses={200: DsbUserCorporateSerializer})
    def put(self, request: Any, *_args: Any, **_kwargs: Any) -> Response:
        """To update a DSB User Corporate instance by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the DSB User Corporate instance.

        **Request Body:**

        * `DsbUserCorporate` object with updated fields.

        **Responses:**

        * `200 OK`: Returns the updated DSB User Corporate instance.
        * `400 Bad Request`: The `identifier` query parameter is required.
        * `404 Not Found`: No DSB User Corporate instance with the given ID was found.

        **Security:**

        * `jwtAuth`, `tokenAuth`, `jwtHeaderAuth`, `jwtCookieAuth`: The request is authenticated using a JSON Web Token.
        """
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response(
                {"detail": "Identifier query parameter is required / no DSB User Corporate instance with the given ID was found."},
                status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_instance(identifier)
        if instance is None:
            return Response(
                {"detail": "No DSB User Corporate instance with the given ID was found."},
                status=status.HTTP_404_NOT_FOUND)

        serializer = DsbUserCorporateSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=DsbUserCorporateSerializer, responses={200: DsbUserCorporateSerializer})
    def patch(self, request: Any, *_args: Any, **_kwargs: Any) -> Response:
        """To partially update a DSB User Corporate instance by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the DSB User Corporate instance.

        **Request Body:**

        * `DsbUserCorporate` object with updated fields.

        **Responses:**

        * `200 OK`: Returns the updated DSB User Corporate instance.
        * `400 Bad Request`: The `identifier` query parameter is required.
        * `404 Not Found`: No DSB User Corporate instance with the given ID was found.

        **Security:**

        * `jwtAuth`, `tokenAuth`, `jwtHeaderAuth`, `jwtCookieAuth`: The request is authenticated using a JSON Web Token.
        """
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response(
                {"detail": "Identifier query parameter is required / invalid identifier."},
                status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_instance(identifier)
        if instance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = DsbUserCorporateSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses={204: None})
    def delete(self, request: Any, *_args: Any, **_kwargs: Any) -> Response:
        """To delete a DSB User Corporate instance by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the DSB User Corporate instance.

        **Responses:**

        * `204 No Content`: DSB User Corporate instance successfully deleted, no response body.
        * `400 Bad Request`: The `identifier` query parameter is required.
        * `404 Not Found`: No DSB User Corporate instance with the given ID was found.

        **Security:**

        * `jwtAuth`, `tokenAuth`, `jwtHeaderAuth`, `jwtCookieAuth`: The request is authenticated using a JSON Web Token.
        """
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response(
                {"detail": "Identifier query parameter is required / invalid identifier."},
                status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_instance(identifier)
        if instance is None:
            return Response(
                {"detail": "No DSB User Corporate instance with the given ID was found."},
                status=status.HTTP_404_NOT_FOUND)

        instance.delete()
        return Response(
            {"detail": "DSB User Corporate instance successfully deleted."},
            status=status.HTTP_204_NO_CONTENT)
