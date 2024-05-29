from django.apps import AppConfig


class DttotDocConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dttotDoc'

    def ready(self):
        import dttotDoc.signals  # noqa