from django.apps import AppConfig


class GuideConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'guide'
    verbose_name = 'Travel Guide'  # Human-readable name for the app

def ready(self):
        import guide.signals  # Register app-specific signals