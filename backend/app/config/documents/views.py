from __future__ import annotations

import logging
from typing import TYPE_CHECKING, ClassVar

from django.db.models.signals import post_save
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.response import Response

from app.common.routers import CustomViewRouter
from app.config.core.models import Document
from app.config.documents.serializers import DocumentSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request

logger = logging.getLogger(__name__)

router = CustomViewRouter()


@router.register_decorator(r"api/documents/list/", name="document-list")
class DocumentListView(GenericAPIView):
    serializer_class = DocumentSerializer
    parser_classes = [JSONParser, MultiPartParser]  # noqa: RUF012
    permission_classes = [permissions.IsAuthenticated]  # noqa: RUF012


    @extend_schema(
        methods=["POST"],
        request=DocumentSerializer,
        responses={201: DocumentSerializer},
    )
    def post(self, request: Request) -> Response:
        context = {"request": request}
        logger.info(f"Request data: {request.data}")  # noqa: G004
        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        document = serializer.save()

        # Prepare context for the signal
        signal_context = {
            "document_id": document.document_id,
        }

        # Emit the signal with the context
        post_save.send_robust(
            sender=Document,
            instance=document,
            created=True,
            context=signal_context,
        )

        logger.info("Document created with ID: %s", document.document_id)

        # Return a custom response message
        return Response(
            {"detail": "We have received the documents. Please sit back and sip some coffee."},
            status=status.HTTP_201_CREATED,
        )


@router.register_decorator(
    r"api/documents/details/$",
    name="document-details",
)
class DocumentDetailView(GenericAPIView):
    serializer_class = DocumentSerializer
    parser_classes: ClassVar[list[type[permissions.BasePermission]]] = [
        JSONParser,
        MultiPartParser,
    ]
    permission_classes: ClassVar[list[type[permissions.BasePermission]]] = [
        permissions.IsAuthenticated,
    ]

    @extend_schema(
        methods=["GET", "PUT", "PATCH", "DELETE"],
        request=DocumentSerializer,
        responses={200: DocumentSerializer},
    )
    def get(self, request: Request) -> Response:
        """To retrieve a document by its ID.

        **Query Parameters:**

        * `document_id`: The unique identifier of the document.

        **Responses:**

        * `200 OK`: Returns the document with the given ID.
        * `400 Bad Request`: The `document_id` query parameter is required.
        * `404 Not Found`: No document with the given ID was found.

        **Security:**

        * `jwtAuth`, `tokenAuth`, `jwtHeaderAuth`, `jwtCookieAuth`: The request is authenticated using a JSON Web Token.
        """
        document_id = request.query_params.get("document_id")
        if not document_id:
            return Response({"detail": "Document ID query parameter is required / invalid identifier."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            document = Document.objects.get(document_id=document_id)
        except Document.DoesNotExist:
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(document)
        return Response(serializer.data)

    def put(self, request: Request) -> Response:
        """To update a document by its ID.

        **Query Parameters:**

        * `document_id`: The unique identifier of the document.

        **Request Body:**

        * `Document` object with updated fields.

        **Responses:**

        * `200 OK`: Returns the updated document.
        * `400 Bad Request`: The `document_id` query parameter is required.
        * `404 Not Found`: No document with the given ID was found.

        **Security:**

        * `jwtAuth`, `tokenAuth`, `jwtHeaderAuth`, `jwtCookieAuth`: The request is authenticated using a JSON Web Token.
        """
        document_id = request.query_params.get("document_id")
        if not document_id:
            return Response({"detail": "Document ID query parameter is required / invalid identifier."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            document = Document.objects.get(document_id=document_id)
        except Document.DoesNotExist:
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)

        context = {"request": request}
        serializer = self.get_serializer(document, data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        document = serializer.save()

        # Update the last_update_by field
        document.last_update_by = request.user
        document.save()

        return Response(serializer.data)

    def patch(self, request: Request) -> Response:
        """To Partially update a document by its ID.

        **Query Parameters:**

        * `document_id`: The unique identifier of the document.

        **Request Body:**

        * `Document` object with updated fields.

        **Responses:**

        * `200 OK`: Returns the updated document.
        * `400 Bad Request`: The `document_id` query parameter is required.
        * `404 Not Found`: No document with the given ID was found.

        **Security:**

        * `jwtAuth`, `tokenAuth`, `jwtHeaderAuth`, `jwtCookieAuth`: The request is authenticated using a JSON Web Token.
        """
        document_id = request.query_params.get("document_id")
        if not document_id:
            return Response({"detail": "Document ID query parameter is required / no document with the given ID was found"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            document = Document.objects.get(document_id=document_id)
        except Document.DoesNotExist:
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)

        context = {"request": request}
        serializer = self.get_serializer(document, data=request.data, partial=True, context=context)
        serializer.is_valid(raise_exception=True)
        document = serializer.save()

        # Update the last_update_by field
        document.last_update_by = request.user
        document.save()

        return Response(serializer.data)

    def delete(self, request: Request) -> Response:
        """To delete a specific document.

        **Query Parameters:**

        * `document_id`: The unique identifier of the document.

        **Responses:**

        * `204 No Content`: Document successfully deleted, no response body.
        * `400 Bad Request`: The `document_id` query parameter is required.
        * `404 Not Found`: No document with the given ID was found.

        **Security:**

        * `jwtAuth`, `tokenAuth`, `jwtHeaderAuth`, `jwtCookieAuth`: The request is authenticated using a JSON Web Token.
        """
        document_id = request.query_params.get("document_id")
        if not document_id:
            return Response({"detail": "Document ID query parameter is required / invalid identifier."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            document = Document.objects.get(document_id=document_id)
        except Document.DoesNotExist:
            return Response({"detail": "Document not found."}, status=status.HTTP_404_NOT_FOUND)

        document.delete()
        return Response({"detail": "Document has been successfully deleted!"}, status=status.HTTP_204_NO_CONTENT)
