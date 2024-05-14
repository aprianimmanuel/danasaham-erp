from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from core.models import dttotDoc, Document
from .serializers import DttotDocSerializer


class DttotDocListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        dttot_docs = dttotDoc.objects.all()
        serializer = DttotDocSerializer(dttot_docs, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = DttotDocSerializer(data=request.data)
        if serializer.is_valid():
            dttot_doc = serializer.save()
            document = get_object_or_404(Document, pk=dttot_doc.document_id)

            # Assuming 'handle_dttot_document' logic is applicable here as part of post-processing
            if document.document_type == 'DTTOT Document':
                try:
                    self.handle_dttot_document(document)
                except ValidationError as e:
                    # Handle processing errors specifically
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
