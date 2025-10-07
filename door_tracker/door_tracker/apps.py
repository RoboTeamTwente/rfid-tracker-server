# door_tracker/apps.py
import threading

from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class DoorTrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'door_tracker'

    def ready(self):
        from .backup_scheduler import start

        # Start scheduler in background thread
        threading.Thread(target=start, daemon=True).start()


class DoorTrackerAdminConfig(AdminConfig):
    default_site = 'door_tracker.admin.DoorTrackerAdminSite'
