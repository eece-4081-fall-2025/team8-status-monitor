from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError
import sys

class StatusMonitorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'status_monitor'

    def ready(self):
       from .tasks import start_scheduler
       try:
           start_scheduler()
       except (OperationalError, ProgrammingError):
           print("Database not ready- scheduler will start after migrations.")