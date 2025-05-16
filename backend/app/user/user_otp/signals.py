from __future__ import annotations
from django.db.models.signals import post_save
from django.dispatch import receiver
from app.user.user_otp.models import UserOTP
from app.user.user_otp.tasks import send_otp_via_email
from app.user.user_otp.logging import otp_logger
from app.user.signals import email_verification_signal


@receiver(email_verification_signal)
def handle_otp_post_save(
    sender,
    user_data,
    **kwargs,
):
    """
    Handle post_save signal for UserOTP model.

    Args:
        sender: The sender of the signal.
        instance (UserOTP): The instance of the UserOTP model.
        created (bool): True if the instance is newly created, False otherwise.

    Returns:
        None

    """
    user_id = user_data.get("user_id")
    if user_id:
        send_otp_via_email.delay(user_id)