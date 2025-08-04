from django.apps import AppConfig


class AlmaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Alma'

from django.apps import AppConfig

class AlmaAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'alma_app'

    def ready(self):
        import alma_app.signals
