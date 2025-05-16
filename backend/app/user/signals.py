from __future__ import annotations

from typing import Any

from django.conf import settings  #type: ignore # noqa: PGH003
from django.db.models.signals import post_save  #type: ignore # noqa: PGH003
from django.dispatch import Signal, receiver  #type: ignore # noqa: PGH003

from app.user.models import User

email_verification_signal = Signal(providing_args=["user_data"])

@receiver(post_save, sender=User)
def emailverify(sender, instance, created, **kwargs):
    if created and instance.email:
        email_verification_signal.send_robust(sender=sender, user_data={"user_id": instance.user_id})

