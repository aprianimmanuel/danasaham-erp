from django.urls import path
from .views import DttotDocDetailView, DttotDocListView

urlpatterns = [
    path(
        'dttotdocs/<uuid:document_id>/',
        DttotDocListView.as_view(),
        name='dttot-doc-list'
    ),
    path(
        'dttotdocs/detail/<uuid:pk>/',
        DttotDocDetailView.as_view(),
        name='dttot-doc-detail'),
]
