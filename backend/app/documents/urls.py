from django.urls import path, include
from .views import (
    DocumentCreateAPIView,
    DocumentListAPIView,
    DocumentDetailAPIView
)

urlpatterns = [
    path(
        'documents/upload/',
        DocumentCreateAPIView.as_view(),
        name='document-create'),
    path(
        'documents/',
        DocumentListAPIView.as_view(),
        name='document-list'),
    path(
        'documents/<uuid:pk>/',
        DocumentDetailAPIView.as_view(),
        name='document-detail'),

    # DTTOT Document API and any other app-specific URLs
    path('documents/', include('dttotDoc.urls')),
]