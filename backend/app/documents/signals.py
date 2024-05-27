from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from core.models import Document

# This signal is sent after a DTTOT Document has been created.
dttot_document_created = Signal(
    providing_args=[
        "instance",
        "created",
        "context"
    ]
)


@receiver(post_save, sender=Document)
def trigger_dttot_processing(sender, instance, created, **kwargs):
    if created and instance.document_type == 'DTTOT Document':
        # Emit custom signal for DTTOT document processing
        context = kwargs.get('context', {})
        dttot_document_created.send(
            sender=instance.__class__,
            instance=instance,
            created=created,
            context=context
        )
