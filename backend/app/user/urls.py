from django.urls import path, re_path
from user.views import (
    CreateUserView,
    UserDetailView,
    LoginView,
    ManageUserView,
    VerifyEmailView
)

app_name = 'user'

urlpatterns = [
    path('create/', CreateUserView.as_view(), name='create'),
    re_path(
        r'^detail/(?P<user_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', 
        UserDetailView.as_view(), 
        name='detail'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    path('me/', ManageUserView.as_view(), name='me'),
]