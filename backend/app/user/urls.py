from django.urls import path
from user.views import (
    CreateUserView,
    UserDetailView,
    LoginView,
    ManageUserView,
    VerifyEmailView,
    UserListView,
    UserProfileDetailView
)

app_name = 'user'

urlpatterns = [
    path('create/', CreateUserView.as_view(), name='create'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    path('list/', UserListView.as_view(), name='list'),
    path('<uuid:user_id>/', UserDetailView.as_view(), name='detail'),
    path('<uuid:user_id>/update/', ManageUserView.as_view(), name='update'),
    path(
        '<uuid:user_id>/profile/',
        UserProfileDetailView.as_view(),
        name='profile')
]
