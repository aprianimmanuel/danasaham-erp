from django.urls import path
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
    path('detail/<uuid:user_id>/', UserDetailView.as_view(), name='detail'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    path('me/', ManageUserView.as_view(), name='me'),
]