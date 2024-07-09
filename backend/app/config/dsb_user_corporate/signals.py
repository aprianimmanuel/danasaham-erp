from __future__ import annotations

from django.dispatch import receiver

from app.config.documents.signals import dsb_user_corporate_document_created
from app.config.dsb_user_corporate.tasks import process_dsb_user_corporate_document

@receiver(dsb_user_corporate_document_created)
def trigger_dsb_user_corporate_processing(
    sender,
    instance,
    created,
    context,
    user_data,
    **kwargs,
) -> None:
    if created:
        process_dsb_user_corporate_document.delay(instance.pk, user_data)