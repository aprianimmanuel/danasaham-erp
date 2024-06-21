from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from django.db import transaction
from app.config.core.models import Document
from app.config.dttotDoc.tasks import process_dttot_document

# Signal is sent after a DTTOT Document has been created.
dttot_document_created = Signal(
    "instance",
    "created",
    "context",
    "user_data"
)

@receiver(post_save, sender=Document)
def trigger_dttot_processing(sender, instance, created, **kwargs):
    if created and instance.document_type == 'DTTOT Document':
        context = kwargs.get('context', {})
        user = instance.created_by
        user_data = {
            'user_id': user.pk,
        }
        transaction.on_commit(
            lambda: dttot_document_created.asend_robust(
                sender=instance.__class__,
                instance=instance,
                created=created,
                context=context,
                user_data=user_data
            )
        )

@receiver(dttot_document_created)
async def handle_dttot_document_created(sender, instance, created, context, user_data, **kwargs):
    if created:
        process_dttot_document.delay(instance.document_id, user_data)


# Signal is sent after a DSB User Personal Document has been created.
dsb_user_personal_document_created = Signal(
    "instance",
    "created",
    "context",
    "user_data"
)

@receiver(post_save, sender=Document)
def trigger_dsb_user_personal_processing(sender, instance, created, **kwargs):
    if created and instance.document_type == 'DSB User Personal List Document':
        context = kwargs.get('context', {})
        user = instance.created_by
        user_data = {
            'user_id': user.pk,
        }
        transaction.on_commit(
            lambda: dsb_user_personal_document_created.asend_robust(
                sender=instance.__class__,
                instance=instance,
                created=created,
                context=context,
                user_data=user_data
            )
        )
