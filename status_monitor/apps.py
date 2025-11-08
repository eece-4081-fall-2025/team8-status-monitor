from django.apps import AppConfig

class StatusMonitorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'status_monitor'

    def ready(self):
        # Start the periodic site-check scheduler
        from .tasks import start_scheduler
        start_scheduler()