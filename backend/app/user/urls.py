"""
URLs for the user API
"""

from django.urls import path
from user import views

app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('mfa/', views.GenerateMFATokenView.as_view(), name='mfa'),
    path('generate-totp/',
         views.GenerateTOTPSecretView.as_view(),
         name='totp_generate'),
    path('verify-totp/',
         views.VerifyTOTPSecretView.as_view(),
         name='totp_verify'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('email-otp/',
         views.SetupEmailOTPView.as_view(),
         name='email_otp_setup')
]
