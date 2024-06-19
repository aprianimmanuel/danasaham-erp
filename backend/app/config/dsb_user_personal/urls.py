# dsb_user_personal/urls.py
from django.urls import path, include
from app.config.dsb_user_personal.views import DsbUserPersonalListView, DsbUserPersonalDetailView


app_name = 'dsb_user_personal'

urlpatterns = [
    path('api/dsb-user-personal/list/', DsbUserPersonalListView.as_view(), name='dsb-user-personal-list'),
    path('api/dsb-user-personal/details/', DsbUserPersonalDetailView.as_view(), name='dsb-user-personal-details')
]
