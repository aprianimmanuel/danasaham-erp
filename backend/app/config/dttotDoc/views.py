import logging
from rest_framework import status, permissions
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from app.config.core.models import dttotDoc
from app.config.dttotDoc.serializers import DttotDocSerializer, DttotDocListSerializer
from app.common.routers import CustomViewRouter

logger = logging.getLogger(__name__)

router = CustomViewRouter(url_prefix="api/")

@router.register_decorator(r"documents/dttotdocs/<uuid:document_id>/", name="dttot-doc-list")
class DttotDocListView(GenericAPIView):
    serializer_class = DttotDocListSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: DttotDocListSerializer}
    )
    def get(self, request, document_id):
        queryset = dttotDoc.objects.filter(document=document_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

@router.register_decorator(r"documents/dttotdocs/<uuid:pk>/", name="dttot-doc-detail")
class DttotDocDetailView(GenericAPIView):
    serializer_class = DttotDocSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: DttotDocSerializer}
    )
    def get(self, request, pk):
        dttot_doc = dttotDoc.objects.get(pk=pk)
        serializer = self.get_serializer(dttot_doc)
        return Response(serializer.data)

    @extend_schema(
        request=DttotDocSerializer,
        responses={200: DttotDocSerializer}
    )
    def put(self, request, pk):
        dttot_doc = dttotDoc.objects.get(pk=pk)
        serializer = self.get_serializer(dttot_doc, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=DttotDocSerializer,
        responses={200: DttotDocSerializer}
    )
    def patch(self, request, pk):
        dttot_doc = dttotDoc.objects.get(pk=pk)
        serializer = self.get_serializer(dttot_doc, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={204: None}
    )
    def delete(self, request, pk):
        dttot_doc = dttotDoc.objects.get(pk=pk)
        dttot_doc.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
