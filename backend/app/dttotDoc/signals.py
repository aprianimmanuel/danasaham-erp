from django.dispatch import receiver
from documents.signals import dttot_document_created
from dttotDoc.utils import handle_dttot_document


@receiver(dttot_document_created)
def process_dttot_document(sender, instance, created, context, **kwargs):
    handle_dttot_document(instance, instance.created_by, context)
