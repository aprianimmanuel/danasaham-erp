from __future__ import annotations

from typing import Any

from django.conf import settings  #type: ignore # noqa: PGH003
from django.db.models.signals import post_save  #type: ignore # noqa: PGH003
from django.dispatch import receiver  #type: ignore # noqa: PGH003

from app.user.models import UserProfile  #type: ignore # noqa: PGH003


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(
    _sender,  # noqa: ANN001
    instance,  # noqa: ANN001
    created,  # noqa: ANN001
    **_kwargs: Any,
) -> None:
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(
    _sender,  # noqa: ANN001
    instance,  # noqa: ANN001
    **_kwargs: Any,
) -> None:
    instance.profile.save()
