from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from .serializers import DttotDocSerializer
from core.models import dttotDoc


class DttotDocListView(ListAPIView):
    serializer_class = DttotDocSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Ensure that document_id is passed correctly as a keyword argument
        document_id = self.kwargs.get('document_id')
        return dttotDoc.objects.filter(document=document_id)

    def get_serializer_context(self):
        """Ensure the request is passed to the serializer."""
        context = super(DttotDocListView, self).get_serializer_context()
        context.update({'request': self.request})
        return context


class DttotDocDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = DttotDocSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        document_id = self.kwargs.get('document_id')
        pk = self.kwargs.get('pk')
        return dttotDoc.objects.filter(
            document__document_id=document_id,
            pk=pk)

    def get_serializer_context(self):
        """Ensure the request is passed to the serializer."""
        context = super(DttotDocDetailAPIView, self).get_serializer_context()
        context.update({'request': self.request})
        return context
