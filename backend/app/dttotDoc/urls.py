from django.urls import path
from .views import DttotDocListView, DttotDocDetailAPIView

urlpatterns = [
    path(
        'dttotdocs/<uuid:document_id>/',
        DttotDocListView.as_view(),
        name='dttot-docs-list'),
    path(
        'dttotdocs/<uuid:document_id>/<uuid:dttot_id>/',
        DttotDocDetailAPIView.as_view(),
        name='dttot-doc-detail'),
]