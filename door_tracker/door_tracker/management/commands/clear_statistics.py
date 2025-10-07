# file: webui/management/commands/clear_statistics.py

from django.core.management.base import BaseCommand
from webui.models import Statistics


class Command(BaseCommand):
    help = 'Delete all statistics from the database'

    def handle(self, *args, **options):
        count, _ = Statistics.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} statistics records.'))
