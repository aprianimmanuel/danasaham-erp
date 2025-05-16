from __future__ import annotations

import logging
from typing import Any, ClassVar

from drf_spectacular.utils import extend_schema  #type: ignore # noqa: PGH003
from rest_framework import permissions, status  #type: ignore # noqa: PGH003
from rest_framework.generics import GenericAPIView  #type: ignore # noqa: PGH003
from rest_framework.response import Response  #type: ignore # noqa: PGH003

from app.common.routers import CustomViewRouter  #type: ignore # noqa: PGH003
from app.documents.dttotDoc.models import DttotDoc  #type: ignore # noqa: PGH003
from app.documents.dttotDoc.serializers import (  #type: ignore # noqa: PGH003
    DttotDocListSerializer,
    DttotDocSerializer,
)
from django.db.models import Q

logger = logging.getLogger(__name__)

router = CustomViewRouter(url_prefix="api/")


@router.register_decorator(
    r"^documents/dttotdocs/list/?$",
    name="dttot-doc-list",
)
class DttotDocListView(GenericAPIView):
    serializer_class = DttotDocListSerializer
    permission_classes: ClassVar[list[type[permissions.BasePermission]]] = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.query_params.get("query")

        if query:
            # Search in name field, alias, description, nik, passport and phone_number
            search_filter = (
                Q(dttot_first_name__icontains=query) |
                Q(dttot_middle_name__icontains=query) |
                Q(dttot_last_name__icontains=query))

            # Alias fields (name and description)
            for i in range(1, 29): # Alias name fields
                search_filter |= Q(**{f"dttot_alias_name_{i}__icontains": query})
                search_filter |= Q(**{f"dttot_alias_first_name_{i}__icontains": query})
                search_filter |= Q(**{f"dttot_alias_middle_name_{i}__icontains": query})
                search_filter |= Q(**{f"dttot_alias_last_name_{i}__icontains": query})

            for j in range(1,10): # description fields
                search_filter |= Q(**{"dttot_description_{j}__icontains": query})

            # Nik and passport
            search_filter |= Q(dttot_nik_ktp__icontains=query)
            search_filter |= Q(dttot_passport_number__icontains=query)

            queryset = queryset.filter(search_filter).distinct()

        return queryset


    @extend_schema(responses={200: DttotDocListSerializer})
    def get(self, request: Any) -> Response:
        """To retrieve a list of DTTOT documents filtered by the document ID if provided.

        **Query Parameters:**

        * `identifier`: The document ID to filter by.

        **Responses:**

        * `200 OK`: Returns a list of `DttotDoc` objects.

        **Security:**

        * `jwtAuth`, `tokenAuth`, `jwtHeaderAuth`, `jwtCookieAuth`: The request is authenticated using a JSON Web Token.
        """
        document_id = request.query_params.get("identifier")
        if document_id:
            logger.info("Fetching DTTOT documents for identifier: %s", document_id)
            queryset = DttotDoc.objects.filter(document=document_id)
        else:
            queryset = DttotDoc.objects.all()

        serializer = self.get_serializer(queryset, many=True)
        logger.info(
            "Successfully fetched %d DTTOT documents.", len(queryset),
        )
        return Response(serializer.data)


@router.register_decorator(
    r"^documents/dttotdocs/details/?$",
    name="dttot-doc-detail",
)
class DttotDocDetailView(GenericAPIView):
    serializer_class = DttotDocSerializer
    permission_classes: ClassVar[list[type[permissions.BasePermission]]] = [permissions.IsAuthenticated]

    def get_instance(
            self,
            identifier: str,
    ) -> DttotDoc:
        """To attempt to retrieve a DTTOT document by either its document ID or its UUID.

        Args:
        ----
            identifier: The document ID or UUID of the DTTOT document to be retrieved.

        Returns:
        -------
            The retrieved DTTOT document, or None if no document with the given identifier was found.

        """
        try:
            instance = DttotDoc.objects.get(
                document=identifier,
            )
        except DttotDoc.DoesNotExist:
            try:
                instance = DttotDoc.objects.get(
                    dttot_id=identifier,
                )
            except DttotDoc.DoesNotExist:
                return None
        return instance

    @extend_schema(responses={200: DttotDocSerializer})
    def get(
        self,
        request: Any,
    ) -> Response:
        """To retrieve a DTTOT document by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the document.

        **Responses:**

        * `200 OK`: Returns the document with the given ID.
        * `400 Bad Request`: The `identifier` query parameter is required.
        * `404 Not Found`: No document with the given ID was found.

        **Security:**

        * `jwtAuth`, `tokenAuth`, `jwtHeaderAuth`, `jwtCookieAuth`: The request is authenticated using a JSON Web Token.
        """
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response({"detail": "Identifier query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        logger.info("Fetching DTTOT document details for ID: %s", identifier)
        instance = self.get_instance(identifier)
        if instance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DttotDocSerializer(instance)
        logger.info("Successfully fetched DTTOT document details for ID: %s", identifier)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=DttotDocSerializer, responses={200: DttotDocSerializer})
    def put(
        self,
        request: Any,
    ) -> Response:
        """To update a DTTOT document by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the document.

        **Request Body:**

        * `DttotDoc` object with updated fields.

        **Responses:**

        * `200 OK`: Returns the updated document.
        * `400 Bad Request`: The `identifier` query parameter is required.
        * `404 Not Found`: No document with the given ID was found.

        **Security:**

        * `jwtAuth`, `tokenAuth`, `jwtHeaderAuth`, `jwtCookieAuth`: The request is authenticated using a JSON Web Token.
        """
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response({"detail": "Identifier query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        logger.info("Updating DTTOT document for ID: %s", identifier)
        instance = self.get_instance(identifier)
        if instance is None:
            return Response(
                {"detail": "No DTTOT document found with the given identifier."},
                status=status.HTTP_404_NOT_FOUND)
        serializer = DttotDocSerializer(
            instance,
            data=request.data,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=DttotDocSerializer, responses={200: DttotDocSerializer})
    def patch(
        self,
        request: Any,
    ) -> Response:
        """To partially update a DTTOT document by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the document.

        **Request Body:**

        * `DttotDoc` object with updated fields.

        **Responses:**

        * `200 OK`: Returns the updated document.
        * `400 Bad Request`: The `identifier` query parameter is required.
        * `404 Not Found`: No document with the given ID was found.

        **Security:**

        * `jwtAuth`, `tokenAuth`, `jwtHeaderAuth`, `jwtCookieAuth`: The request is authenticated using a JSON Web Token.
        """
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response({"detail": "Identifier query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        logger.info("Partially updating DTTOT document for ID: %s", identifier)
        instance = self.get_instance(identifier)
        if instance is None:
            return Response(
                {"error": "No DTTOT document found with the given identifier."},
                status=status.HTTP_404_NOT_FOUND)
        serializer = DttotDocSerializer(
            instance,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses={204: None})
    def delete(
        self,
        request: Any,
    ) -> Response:
        """To delete a DTTOT document by its ID.

        **Query Parameters:**

        * `identifier`: The unique identifier of the document.

        **Responses:**

        * `204 No Content`: Document successfully deleted, no response body.
        * `400 Bad Request`: The `identifier` query parameter is required.
        * `404 Not Found`: No document with the given ID was found.

        **Security:**

        * `jwtAuth`, `tokenAuth`, `jwtHeaderAuth`, `jwtCookieAuth`: The request is authenticated using a JSON Web Token.
        """
        identifier = request.query_params.get("identifier")
        if not identifier:
            return Response({"detail": "Identifier query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        logger.info("Deleting DTTOT document for ID: %s", identifier)
        instance = self.get_instance(identifier)
        if instance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        logger.info("Successfully deleted DTTOT document for ID: %s", identifier)
        return Response(
            {"detail": "Successfully deleted DTTOT document for ID"},
            status=status.HTTP_204_NO_CONTENT)
