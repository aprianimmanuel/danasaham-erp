import logging
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework import status, permissions
from documents.serializers import DocumentSerializer
from core.models import Document
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)
from drf_spectacular.utils import extend_schema
from django.db.models.signals import post_save

logger = logging.getLogger(__name__)


@extend_schema(
    methods=['POST'],
    request=DocumentSerializer,
    responses={201: DocumentSerializer}
)
class DocumentAPIView(ListCreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = [JSONParser, MultiPartParser]
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
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
            context=context)

        if document.document_type == 'DTTOT Document':
            response_data = {
                'document': serializer.data,
                'dttot_doc': "Processing started"
            }
            logger.info(f"Response data: {response_data}")
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class DocumentDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
