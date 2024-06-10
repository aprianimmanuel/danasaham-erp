from django.dispatch import receiver
from app.config.documents.signals import dttot_document_created
from app.config.documents.dttotDoc.tasks import process_dttot_document_workflow


@receiver(dttot_document_created)
def process_dttot_document(sender, instance, created, context, **kwargs):
    process_dttot_document_workflow.delay(instance.pk)
