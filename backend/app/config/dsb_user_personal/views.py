from __future__ import annotations

from typing import ClassVar, Any

from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.common.routers import CustomViewRouter
from app.config.core.models import dsb_user_personal
from app.config.dsb_user_personal.serializers import DsbUserPersonalSerializer

router = CustomViewRouter(url_prefix="api/")


@router.register_decorator(r"dsb-user-personal/list/", name="dsb-user-personal-list")
class DsbUserPersonalListView(APIView):
    permission_classes: ClassVar = [permissions.IsAuthenticated]

    @extend_schema(responses={200: DsbUserPersonalSerializer(many=True)})
    def get(self, _request: Any, *_args: Any, **_kwargs: Any) -> Response:
        queryset = dsb_user_personal.objects.all()
        serializer = DsbUserPersonalSerializer(queryset, many=True)
        return Response(serializer.data)


@router.register_decorator(
    r"dsb-user-personal/details/<uuid:dsb_user_personal_id>/",
    name="dsb-user-personal-details",
)
class DsbUserPersonalDetailView(APIView):
    permission_classes: ClassVar = [permissions.IsAuthenticated]

    @extend_schema(responses={200: DsbUserPersonalSerializer})
    def get(
        self,
        _request: Any,
        dsb_user_personal_id: str,
        *_args: Any,
        **_kwargs: Any,
    ) -> Response:
        try:
            instance = dsb_user_personal.objects.get(
                dsb_user_personal_id=dsb_user_personal_id,
            )
        except dsb_user_personal.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DsbUserPersonalSerializer(instance)
        return Response(serializer.data)

    @extend_schema(
        request=DsbUserPersonalSerializer,
        responses={200: DsbUserPersonalSerializer},
    )
    def put(
        self,
        request: Any,
        dsb_user_personal_id: str,
        *_args: Any,
        **_kwargs: Any,
    ) -> Response:
        try:
            instance = dsb_user_personal.objects.get(
                dsb_user_personal_id=dsb_user_personal_id,
            )
        except dsb_user_personal.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DsbUserPersonalSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=DsbUserPersonalSerializer,
        responses={200: DsbUserPersonalSerializer},
    )
    def patch(
        self,
        request: Any,
        dsb_user_personal_id: str,
        *_args: Any,
        **_kwargs: Any,
    ) -> Response:
        try:
            instance = dsb_user_personal.objects.get(
                dsb_user_personal_id=dsb_user_personal_id,
            )
        except dsb_user_personal.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DsbUserPersonalSerializer(
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
        dsb_user_personal_id: str,
        *_args: Any,
        **_kwargs: Any,
    ) -> Response:
        try:
            instance = dsb_user_personal.objects.get(
                dsb_user_personal_id=dsb_user_personal_id,
            )
        except dsb_user_personal.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
