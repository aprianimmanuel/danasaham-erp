from django.urls import path
from .views import DocumentAPIView, DocumentDetailAPIView
from app.common.routers import CustomViewRouter

router = CustomViewRouter(url_prefix="api/")

router.register(
    route='documents/',
    view=DocumentAPIView,
    name='document-create'
)

router.register(
    route='documents/<uuid:pk>/',
    view=DocumentDetailAPIView,
    name='document-detail'
)

urlpatterns = router.urls