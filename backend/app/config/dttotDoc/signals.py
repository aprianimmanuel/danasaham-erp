from django.dispatch import receiver
from app.config.documents.signals import dttot_document_created
from app.config.dttotDoc.tasks import process_dttot_document_workflow


@receiver(dttot_document_created)
def process_dttot_document(sender, instance, created, context, user_id, **kwargs):
    process_dttot_document_workflow.delay(instance.pk, user_id)
