from __future__ import annotations
from django.core.mail import send_mail
from app.user.user_otp.logging import otp_logger
from celery import shared_task
from app.user.models import User
from django.utils.crypto import get_random_string
from django.utils import timezone
from app.user.user_otp.models import UserOTP
from datetime import timedelta


@shared_task
def send_otp_via_email(user_id):
    try:
        user = User.objects.get(user_id=user_id)
        otp_code = get_random_string(10, allowed_chars="ABCDEFGHJKLMNPQRSTUVWXYZ23456789")

        # Buat OTP baru
        otp = UserOTP.objects.create(
            user=user,
            otp_code=otp_code,
            otp_type="OTPType.EMAIL_VERIFICATION",
            status_used=False,
            expires_at=timezone.now() + timedelta(minutes=5),
        )

        send_mail(
            subject="OTP Verification",
            message=f"Your OTP code is: {otp_code}",
            from_email="testlab@danasaham.co.id",
            recipient_list=[user.email],
            fail_silently=False,
        )

        otp_logger.info(f"[OTP EMAIL SENT] to={user.email}, otp={otp_code}")
    except User.DoesNotExist as e:
        otp_logger.error(f"[OTP EMAIL FAILED] to={user.email}, otp={otp_code}, error={e}")
        pass