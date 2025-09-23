# door_tracker/backup_scheduler.py
import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command
from django_apscheduler.jobstores import DjangoJobStore

logger = logging.getLogger(__name__)


def backup_website_job():
    logger.info('Running backup_website command...')
    call_command('backup_website')


def start():
    # Only start in the main process (avoid autoreloader double-start)
    if os.environ.get('RUN_MAIN') != 'true':
        return

    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'default')

    # For testing: every minute
    scheduler.add_job(
        backup_website_job,
        trigger='cron',
        hour='23',
        minute='59',
        id='backup_website_job',
        replace_existing=True,
    )

    scheduler.start()
    logger.info('Scheduler started!')
