from django.dispatch import receiver
from app.config.documents.signals import dttot_document_created
from app.config.dttotDoc.tasks import process_dttot_document


@receiver(dttot_document_created)
def process_dttot_document_signal(sender, instance, created, context, user_data, **kwargs):
    process_dttot_document.delay(instance.pk, user_data)
