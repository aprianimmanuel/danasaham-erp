from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DttotDocViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'dttotdocs', DttotDocViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
