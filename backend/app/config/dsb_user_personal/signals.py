from django.db.models.signals import post_save
from django.dispatch import receiver
from app.config.core.models import Document
from app.config.dsb_user_personal.tasks import process_dsb_user_personal_document

@receiver(post_save, sender=Document)
def trigger_dsb_user_personal_processing(sender, instance, created, **kwargs):
    if created and instance.document_type == 'DSB User Personal List Document':
        process_dsb_user_personal_document.delay(instance.pk)