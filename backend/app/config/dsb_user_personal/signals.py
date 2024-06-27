from django.dispatch import receiver
from app.config.documents.signals import dsb_user_personal_document_created
from app.config.dsb_user_personal.tasks import process_dsb_user_personal_document

@receiver(dsb_user_personal_document_created)
def trigger_dsb_user_personal_processing(sender, instance, created, context, user_data, **kwargs):
    if created:
        process_dsb_user_personal_document.delay(instance.pk, user_data)