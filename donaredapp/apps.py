from django.apps import AppConfig


class DonaredappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'donaredapp'

    def ready(self):
        import donaredapp.signals  # Import your signals
