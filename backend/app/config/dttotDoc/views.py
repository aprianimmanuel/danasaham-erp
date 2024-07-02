from __future__ import annotations

import logging
from typing import Any, ClassVar

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
    permission_classes: ClassVar[list[type[permissions.BasePermission]]] = [permissions.IsAuthenticated]

    @extend_schema(responses={200: DttotDocListSerializer})
    def get(self, _request: Any, document_id: str) -> Response:
        logger.info("Fetching DTTOT documents for document ID: %s", document_id)
        queryset = dttotDoc.objects.filter(document=document_id)
        serializer = self.get_serializer(queryset, many=True)
        logger.info(
            "Successfully fetched %d DTTOT documents for document ID: %s", len(queryset), document_id,
        )
        return Response(serializer.data)


@router.register_decorator(
    r"documents/dttotdocs/details/<uuid:dttot_id>/",
    name="dttot-doc-detail",
)
class DttotDocDetailView(GenericAPIView):
    serializer_class = DttotDocSerializer
    permission_classes: ClassVar[list[type[permissions.BasePermission]]] = [permissions.IsAuthenticated]

    @extend_schema(responses={200: DttotDocSerializer})
    def get(self, _request: Any, dttot_id: str) -> Response:
        logger.info("Fetching DTTOT document details for DTTOT ID: %s", dttot_id)
        dttot_doc = dttotDoc.objects.get(dttot_id=dttot_id)
        serializer = self.get_serializer(dttot_doc)
        logger.info(
            "Successfully fetched DTTOT document details for DTTOT ID: %s", dttot_id,
        )
        return Response(serializer.data)

    @extend_schema(request=DttotDocSerializer, responses={200: DttotDocSerializer})
    def put(self, _request: Any, dttot_id: str) -> Response:
        logger.info("Updating DTTOT document for DTTOT ID: %s", dttot_id)
        dttot_doc = dttotDoc.objects.get(dttot_id=dttot_id)
        serializer = self.get_serializer(dttot_doc, data=_request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Successfully updated DTTOT document for DTTOT ID: %s", dttot_id)
            return Response(serializer.data)
        logger.error(
            "Failed to update DTTOT document for DTTOT ID: %s, errors: %s", dttot_id, serializer.errors,
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=DttotDocSerializer, responses={200: DttotDocSerializer})
    def patch(self, _request: Any, dttot_id: str) -> Response:
        logger.info("Partially updating DTTOT document for DTTOT ID: %s", dttot_id)
        dttot_doc = dttotDoc.objects.get(dttot_id=dttot_id)
        serializer = self.get_serializer(dttot_doc, data=_request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(
                "Successfully partially updated DTTOT document for DTTOT ID: %s", dttot_id,
            )
            return Response(serializer.data)
        logger.error(
            "Failed to partially update DTTOT document for DTTOT ID: %s, errors: %s", dttot_id, serializer.errors,
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses={204: None})
    def delete(self, _request: Any, dttot_id: str) -> Response:
        logger.info("Deleting DTTOT document for DTTOT ID: %s", dttot_id)
        dttot_doc = dttotDoc.objects.get(dttot_id=dttot_id)
        dttot_doc.delete()
        logger.info("Successfully deleted DTTOT document for DTTOT ID: %s", dttot_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
