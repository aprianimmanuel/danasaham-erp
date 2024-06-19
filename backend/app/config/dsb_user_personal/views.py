from rest_framework import permissions
from app.config.core.models import dsb_user_personal
from app.config.dsb_user_personal.serializers import DsbUserPersonalSerializer
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app.common.routers import CustomViewRouter

router = CustomViewRouter()


@router.register_decorator(r"dsb_user_personal/", name="dsb_user_personal-list")
class DsbUserPersonalListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: DsbUserPersonalSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        queryset = dsb_user_personal.objects.all()
        serializer = DsbUserPersonalSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=DsbUserPersonalSerializer,
        responses={201: DsbUserPersonalSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = DsbUserPersonalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@router.register_decorator(r"dsb_user_personal/<uuid:pk>/", name="dsb_user_personal-details")
class DsbUserPersonalDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: DsbUserPersonalSerializer}
    )
    def get(self, request, pk, *args, **kwargs):
        try:
            instance = dsb_user_personal.objects.get(pk=pk)
        except dsb_user_personal.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DsbUserPersonalSerializer(instance)
        return Response(serializer.data)

    @extend_schema(
        request=DsbUserPersonalSerializer,
        responses={200: DsbUserPersonalSerializer}
    )
    def put(self, request, pk, *args, **kwargs):
        try:
            instance = dsb_user_personal.objects.get(pk=pk)
        except dsb_user_personal.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DsbUserPersonalSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=DsbUserPersonalSerializer,
        responses={200: DsbUserPersonalSerializer}
    )
    def patch(self, request, pk, *args, **kwargs):
        try:
            instance = dsb_user_personal.objects.get(pk=pk)
        except dsb_user_personal.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DsbUserPersonalSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={204: None}
    )
    def delete(self, request, pk, *args, **kwargs):
        try:
            instance = dsb_user_personal.objects.get(pk=pk)
        except dsb_user_personal.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
