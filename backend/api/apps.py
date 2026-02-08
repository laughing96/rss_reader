from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        try:
            from .services import add_default_feeds
            add_default_feeds()
        except (OperationalError, ProgrammingError):
            # Database not ready yet (migrations not run)
            pass
