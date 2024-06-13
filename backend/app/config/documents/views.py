from __future__ import annotations

import logging
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import GenericAPIView
from app.config.documents.serializers import DocumentSerializer
from app.config.core.models import Document
from drf_spectacular.utils import extend_schema
from django.db.models.signals import post_save
from app.common.routers import CustomViewRouter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rest_framework.request import Request

logger = logging.getLogger(__name__)

router = CustomViewRouter()

@router.register_decorator(r"documents/", name="document-list")
class DocumentListView(GenericAPIView):
    serializer_class = DocumentSerializer
    parser_classes = [JSONParser, MultiPartParser]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        documents = Document.objects.all()
        serializer = self.get_serializer(documents, many=True)
        return Response(serializer.data)

    @extend_schema(
        methods=['POST'],
        request=DocumentSerializer,
        responses={201: DocumentSerializer}
    )
    def post(self, request: Request) -> Response:
        context = {'request': request}
        logger.info(f"Request data: {request.data}")
        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        document = serializer.save()

        # Emit the signal with the context
        post_save.send(
            sender=Document,
            instance=document,
            created=True,
            context=context
        )

        if document.document_type == 'DTTOT Document':
            response_data = {
                'document': serializer.data,
                'dttot_doc': "Processing started"
            }
            logger.info(f"Response data: {response_data}")
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.data, status=status.HTTP_201_CREATED)


@router.register_decorator(r"documents/<uuid:pk>/", name="document-details")
class DocumentDetailView(GenericAPIView):
    serializer_class = DocumentSerializer
    parser_classes = [JSONParser, MultiPartParser]
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        methods=['GET', 'PUT', 'PATCH', 'DELETE'],
        request=DocumentSerializer,
        responses={200: DocumentSerializer}
    )
    def get(self, request: Request, pk: str) -> Response:
        document = Document.objects.get(pk=pk)
        serializer = self.get_serializer(document)
        return Response(serializer.data)

    def put(self, request: Request, pk: str) -> Response:
        document = Document.objects.get(pk=pk)
        serializer = self.get_serializer(document, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request: Request, pk: str) -> Response:
        document = Document.objects.get(pk=pk)
        serializer = self.get_serializer(document, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request: Request, pk: str) -> Response:
        document = Document.objects.get(pk=pk)
        document.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

