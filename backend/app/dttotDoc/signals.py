from django.dispatch import receiver
from documents.signals import dttot_document_created
from .utils import handle_dttot_document
from core.models import Document


@receiver(dttot_document_created)
def process_dttot_document(sender, instance, created, **kwargs):
    if created:
        handle_dttot_document(instance, instance.created_by)
