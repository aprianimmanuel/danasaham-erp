from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet

router = DefaultRouter()
router.register(r'documents', DocumentViewSet)

urlpatterns = [

    # Document API URLs
    path('', include(router.urls)),

    # DTTOT Document API and any other app-specific URLs
    path('documents/', include('dttotDoc.urls')),

]
