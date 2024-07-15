from __future__ import annotations

from typing import ClassVar, Any

from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.common.routers import CustomViewRouter
from app.config.core.models import dsb_user_corporate
from app.config.dsb_user_corporate.serializers import DsbUserCorporateSerializer

router = CustomViewRouter(url_prefix="api/")

@router.register_decorator(r"dsb-user-corporate/list/", name="dsb-user-corporate-list")
class DsbUserCorporateListView(APIView):
    permission_classes: ClassVar = [permissions.IsAuthenticated]

    @extend_schema(responses={200: DsbUserCorporateSerializer(many=True)})
    def get(self, _request: Any, *_args: Any, **_kwargs:Any) -> Response:
        queryset = dsb_user_corporate.objects.all()
        serializer = DsbUserCorporateSerializer(queryset, many=True)
        return Response(serializer.data)


@router.register_decorator(
    r"dsb-user-corporate/details/<uuid:dsb_user_corporate_id/",
    name="dsb-user-corporate-details",
)
class DsbUserCorporateDetailView(APIView):
    permissions_classes: ClassVar = [permissions.IsAuthenticated]

    @extend_schema(responses={200: DsbUserCorporateSerializer})
    def get(
        self,
        _request: Any,
        dsb_user_corporate_id: str,
        *_args: Any,
        **_kwargs: Any,
    ) -> Response:
        try:
            instance = dsb_user_corporate.objects.get(
                dsb_user_corporate_id=dsb_user_corporate_id,
            )
        except dsb_user_corporate.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DsbUserCorporateSerializer(instance)
        return Response(serializer.data)

    @extend_schema(
        request=DsbUserCorporateSerializer,
        responses={200: DsbUserCorporateSerializer},
    )
    def put(
        self,
        request: Any,
        dsb_user_corporate_id: str,
        *_args: Any,
        **_kwargs: Any,
    ) -> Response:
        try:
            instance = dsb_user_corporate.objects.get(
                dsb_user_corporate_id=dsb_user_corporate_id,
            )
        except dsb_user_corporate.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DsbUserCorporateSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=DsbUserCorporateSerializer,
        responses={200: DsbUserCorporateSerializer},
    )
    def patch(
        self,
        request: Any,
        dsb_user_corporate_id: str,
        *_args: Any,
        **_kwargs: Any,
    ) -> Response:
        try:
            instance = dsb_user_corporate.objects.get(
                dsb_user_corporate_id=dsb_user_corporate_id,
            )
        except dsb_user_corporate.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = DsbUserCorporateSerializer(
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
        dsb_user_corporate_id: str,
        *_args: Any,
        **_kwargs: Any,
    ) -> Response:
        try:
            instance = dsb_user_corporate.objects.get(
                dsb_user_corporate_id=dsb_user_corporate_id,
            )
        except dsb_user_corporate.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
