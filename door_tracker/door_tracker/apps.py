# door_tracker/apps.py
import threading

from django.apps import AppConfig


class DoorTrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'door_tracker'

    def ready(self):
        from .backup_scheduler import start

        # Start scheduler in background thread
        threading.Thread(target=start, daemon=True).start()
