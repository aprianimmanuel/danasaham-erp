import logging
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.exceptions import ValidationError
from .serializers import (
    DocumentSerializer,
    DocumentCreateSerializer)
from dttotDoc.serializers import DttotDocSerializer
from core.models import Document
from rest_framework.generics import (
    RetrieveUpdateDestroyAPIView,
    ListAPIView
)

logger = logging.getLogger(__name__)


class DocumentCreateAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data.copy()  # Make a mutable copy of the request data
        document_serializer = DocumentCreateSerializer(
            data=data,
            context={'request': request}
        )

        if document_serializer.is_valid():
            document = document_serializer.save()
            # Check if it's a DTTOT Document and proceed accordingly
            if data.get('document_type') == 'DTTOT Document':
                # Process or handle the DTTOT document specifics
                data['document'] = document.document_id  # Link the DTTOT document to the created document
                dttot_serializer = DttotDocSerializer(data=data, context={'request': request})
                if dttot_serializer.is_valid():
                    dttot_serializer.save()
                    return Response(dttot_serializer.data, status=status.HTTP_201_CREATED)
                else:
                    # If DTTOT handling fails, still return the basic document details with errors
                    response_data = document_serializer.data
                    response_data.update(dttot_serializer.errors)
                    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Normal document creation flow
                return Response(document_serializer.data, status=status.HTTP_201_CREATED)

        return Response(document_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DocumentListAPIView(ListAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]


class DocumentDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]