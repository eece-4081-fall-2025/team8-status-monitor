from django.apps import AppConfig
import sys

class StatusMonitorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'status_monitor'

    def ready(self):
        if 'runserver' in sys.argv:
            from .tasks import start_scheduler
            start_scheduler()