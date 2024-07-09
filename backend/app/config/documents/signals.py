from __future__ import annotations

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver

from app.config.core.models import Document


# Signal is sent after a DTTOT Document has been created.
dttot_document_created = Signal(
    providing_args=["instance", "created", "context", "user_data"],
)


@receiver(post_save, sender=Document)
def trigger_dttot_processing(sender, instance, created, **kwargs) -> None:
    if created and instance.document_type == "DTTOT Document":
        context = kwargs.get("context", {})
        user = instance.created_by
        user_data = {
            "user_id": user.pk,
        }
        transaction.on_commit(
            lambda: dttot_document_created.send_robust(
                sender=instance.__class__,
                instance=instance,
                created=created,
                context=context,
                user_data=user_data,
            ),
        )


# Signal is sent after a DSB User Personal Document has been created.
dsb_user_personal_document_created = Signal(
    providing_args=["instance", "created", "context", "user_data"],
)


@receiver(post_save, sender=Document)
def trigger_dsb_user_personal_processing(sender, instance, created, **kwargs) -> None:
    if created and instance.document_type == "DSB User Personal List Document":
        context = kwargs.get("context", {})
        user = instance.created_by
        user_data = {
            "user_id": user.pk,
        }
        transaction.on_commit(
            lambda: dsb_user_personal_document_created.send_robust(
                sender=instance.__class__,
                instance=instance,
                created=created,
                context=context,
                user_data=user_data,
            ),
        )


#Signal is sent after a DSB User Corporate Document has been created
dsb_user_corporate_document_created = Signal(
    providing_args=["instance", "created", "context", "user_data"],
)


@receiver(post_save, sender=Document)
def trigger_dsb_user_corporate_processing(sender, instance, created, **kwargs) -> None:
    if created and instance.document_type == "DSB User Corporate List Document":
        context = kwargs.get("context", {})
        user = instance.created_by
        user_data = {
            "user_id": user.pk
        }
        transaction.on_commit(
            lambda: dsb_user_corporate_document_created.send_robust(
                sender=instance.__class__,
                instance=instance,
                created=created,
                context=context,
                user_data=user_data
            ),
        )
