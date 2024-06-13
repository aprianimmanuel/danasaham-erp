from django.urls import path
from app.config.documents.views import DocumentListView, DocumentDetailView

app_name = 'documents'

urlpatterns = [
    path('api/documents/', DocumentListView.as_view(), name='document-list'),
    path('api/documents/<uuid:pk>/', DocumentDetailView.as_view(), name='document-details'),
]