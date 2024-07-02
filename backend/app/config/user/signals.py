from __future__ import annotations

from typing import Any

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from app.config.core.models import UserProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(
    _sender: type[settings.AUTH_USER_MODEL],
    instance: settings.AUTH_USER_MODEL,
    created: True,
    **_kwargs: Any,
) -> None:
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(
    _sender: type[settings.AUTH_USER_MODEL],
    instance: settings.AUTH_USER_MODEL,
    **_kwargs: Any,
) -> None:
    instance.profile.save()
