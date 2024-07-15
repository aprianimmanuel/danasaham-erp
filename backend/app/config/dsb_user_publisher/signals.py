from __future__ import annotations

from django.dispatch import receiver

from app.config.documents.signals import dsb_user_publisher_document_created
from app.config.dsb_user_publisher.tasks import process_dsb_user_publisher_document


@receiver(dsb_user_publisher_document_created)
def trigger_dsb_user_publisher_processing(
    sender,
    instance,
    created,
    context,
    user_data,
    **kwargs,
) -> None:
    if created:
        process_dsb_user_publisher_document.delay(instance.pk, user_data)
