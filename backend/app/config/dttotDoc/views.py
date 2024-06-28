from __future__ import annotations

import logging

from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from app.common.routers import CustomViewRouter
from app.config.core.models import dttotDoc
from app.config.dttotDoc.serializers import DttotDocListSerializer, DttotDocSerializer

logger = logging.getLogger(__name__)

router = CustomViewRouter(url_prefix="api/")


@router.register_decorator(
    r"documents/dttotdocs/list/<uuid:document_id>/",
    name="dttot-doc-list",
)
class DttotDocListView(GenericAPIView):
    serializer_class = DttotDocListSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: DttotDocListSerializer})
    def get(self, request, document_id):
        logger.info(f"Fetching DTTOT documents for document ID: {document_id}")
        queryset = dttotDoc.objects.filter(document=document_id)
        serializer = self.get_serializer(queryset, many=True)
        logger.info(
            f"Successfully fetched {len(queryset)} DTTOT documents for document ID: {document_id}",
        )
        return Response(serializer.data)


@router.register_decorator(
    r"documents/dttotdocs/details/<uuid:dttot_id>/",
    name="dttot-doc-detail",
)
class DttotDocDetailView(GenericAPIView):
    serializer_class = DttotDocSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: DttotDocSerializer})
    def get(self, request, dttot_id):
        logger.info(f"Fetching DTTOT document details for DTTOT ID: {dttot_id}")
        dttot_doc = dttotDoc.objects.get(dttot_id=dttot_id)
        serializer = self.get_serializer(dttot_doc)
        logger.info(
            f"Successfully fetched DTTOT document details for DTTOT ID: {dttot_id}",
        )
        return Response(serializer.data)

    @extend_schema(request=DttotDocSerializer, responses={200: DttotDocSerializer})
    def put(self, request, dttot_id):
        logger.info(f"Updating DTTOT document for DTTOT ID: {dttot_id}")
        dttot_doc = dttotDoc.objects.get(dttot_id=dttot_id)
        serializer = self.get_serializer(dttot_doc, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Successfully updated DTTOT document for DTTOT ID: {dttot_id}")
            return Response(serializer.data)
        logger.error(
            f"Failed to update DTTOT document for DTTOT ID: {dttot_id}, errors: {serializer.errors}",
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=DttotDocSerializer, responses={200: DttotDocSerializer})
    def patch(self, request, dttot_id):
        logger.info(f"Partially updating DTTOT document for DTTOT ID: {dttot_id}")
        dttot_doc = dttotDoc.objects.get(dttot_id=dttot_id)
        serializer = self.get_serializer(dttot_doc, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(
                f"Successfully partially updated DTTOT document for DTTOT ID: {dttot_id}",
            )
            return Response(serializer.data)
        logger.error(
            f"Failed to partially update DTTOT document for DTTOT ID: {dttot_id}, errors: {serializer.errors}",
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses={204: None})
    def delete(self, request, dttot_id):
        logger.info(f"Deleting DTTOT document for DTTOT ID: {dttot_id}")
        dttot_doc = dttotDoc.objects.get(dttot_id=dttot_id)
        dttot_doc.delete()
        logger.info(f"Successfully deleted DTTOT document for DTTOT ID: {dttot_id}")
        return Response(status=status.HTTP_204_NO_CONTENT)
