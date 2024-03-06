from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.models import dttotDoc
from .serializers import DttotDocSerializer


class DttotDocViewSet(viewsets.ModelViewSet):
    queryset = dttotDoc.objects.all()
    serializer_class = DttotDocSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(input_by=self.request.user)
