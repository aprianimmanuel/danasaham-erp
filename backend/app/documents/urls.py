from django.urls import path, include
from .views import (
    DocumentAPIView,
    DocumentDetailAPIView
)

urlpatterns = [
    path(
        'documents/',
        DocumentAPIView.as_view(),
        name='document-create'),
    path(
        'documents/<uuid:pk>/',
        DocumentDetailAPIView.as_view(),
        name='document-detail'),

    # DTTOT Document API and any other app-specific URLs
    path('documents/', include('dttotDoc.urls')),
]