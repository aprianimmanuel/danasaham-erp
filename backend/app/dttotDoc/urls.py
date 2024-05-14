from django.urls import path
from .views import DttotDocListCreateAPIView

urlpatterns = [
    path('dttotdocs/', DttotDocListCreateAPIView.as_view(), name='dttotdocs-create'),
]
