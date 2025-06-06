import logging
from django.dispatch import Signal

logger = logging.getLogger(__name__)

dttot_doc_report_status_failed = Signal()
dttot_doc_report_status_done = Signal()

def handle_status_failed(sender, instance, **kwargs):
  """Handles the DttotDocReport status changed to FAILED event."""
  logger.info(f"DttotDocReport status changed to FAILED for instance: {instance.id}")

def handle_status_done(sender, instance, **kwargs):
  """Handles the DttotDocReport status changed to DONE event."""
  logger.info(f"DttotDocReport status changed to DONE for instance: {instance.id}")
