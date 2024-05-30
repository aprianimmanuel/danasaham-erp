from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import DttotDocSerializer, DttotDocListSerializer
from core.models import dttotDoc


class DttotDocListView(ListAPIView):
    serializer_class = DttotDocListSerializer
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


class DttotDocDetailView(APIView):
    def get(self, request, pk):
        dttot_doc = dttotDoc.objects.get(pk=pk)
        serializer = DttotDocSerializer(dttot_doc)
        return Response(serializer.data)

    def put(self, request, pk):
        dttot_doc = dttotDoc.objects.get(pk=pk)
        serializer = DttotDocSerializer(dttot_doc, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        dttot_doc = dttotDoc.objects.get(pk=pk)
        serializer = DttotDocSerializer(
            dttot_doc,
            data=request.data,
            partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        dttot_doc = dttotDoc.objects.get(pk=pk)
        dttot_doc.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
