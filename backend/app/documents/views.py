from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from core.models import Document
from .serializers import DocumentSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Additional logic for OCR and model enhancements would go here.
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user)

    def update(self, request, *args, **kwargs):
        document = self.get_object()
        serializer = self.get_serializer(
            document, data=request.data, partial=True)
        if serializer.is_valid():
            # This is where you'd include logic for file processing, OCR, etc.
            serializer.save(updated_by=self.request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
