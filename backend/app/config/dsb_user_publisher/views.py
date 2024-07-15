from __future__ import annotations

from typing import Any, ClassVar

from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.common.routers import CustomViewRouter
from app.config.core.models import dsb_user_publisher
from app.config.dsb_user_publisher.serializers import DsbUserPublisherSerializer

router = CustomViewRouter(url_prefix="api/")

@router.register_decorator(r"dsb-user-publisher/list/", name="dsb-user-publisher-list")
class DsbUserPublisherListView(APIView):
    permission_classes: ClassVar = [permissions.IsAuthenticated]

    @extend_schema(responses={200: DsbUserPublisherSerializer(many=True)})
    def get(self, _request: Any, *_args: Any, **_kwargs: Any) -> Response:
        queryset = dsb_user_publisher.objects.all()
        serializer = DsbUserPublisherSerializer(queryset, many=True)
        return Response(serializer.data)

@router.register_decorator(
    r"dsb-user-publisher/details/<uuid:dsb_user_publisher_id>/",
    name="dsb-user-publisher-details",
)
class DsbUserPublisherDetailView(APIView):
    permission_classes: ClassVar = [permissions.IsAuthenticated]

    @extend_schema(responses={200: DsbUserPublisherSerializer})
    def get(
        self,
        _request: Any,
        dsb_user_publisher_id: str,
        *_args: Any,
        **_kwargs: Any,
    ) -> Response:
        try:
            instance = dsb_user_publisher.objects.get(
                dsb_user_publisher_id=dsb_user_publisher_id,
            )
        except dsb_user_publisher.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DsbUserPublisherSerializer(instance)
        return Response(serializer.data)

    @extend_schema(
        request=DsbUserPublisherSerializer,
        responses={200: DsbUserPublisherSerializer},
    )
    def put(
        self,
        request: Any,
        dsb_user_publisher_id: str,
        *_args: Any,
        **_kwargs: Any,
    ) -> Response:
        try:
            instance = dsb_user_publisher.objects.get(
                dsb_user_publisher_id=dsb_user_publisher_id,
            )
        except dsb_user_publisher.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DsbUserPublisherSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=DsbUserPublisherSerializer,
        responses={200: DsbUserPublisherSerializer},
    )
    def patch(
        self,
        request: Any,
        dsb_user_publisher_id: str,
        *_args: Any,
        **_kwargs: Any,
    ) -> Response:
        try:
            instance = dsb_user_publisher.objects.get(
                dsb_user_publisher_id=dsb_user_publisher_id,
            )
        except dsb_user_publisher.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DsbUserPublisherSerializer(
            instance,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses={204: None})
    def delete(
        self,
        _request: Any,
        dsb_user_publisher_id: str,
        *_args: Any,
        **_kwargs: Any,
    ) -> Response:
        try:
            instance = dsb_user_publisher.objects.get(
                dsb_user_publisher_id=dsb_user_publisher_id,
            )
        except dsb_user_publisher.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

