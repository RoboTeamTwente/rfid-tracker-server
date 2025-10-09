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


def update_statistics_job():
    logger.info('Updating statistics…')
    call_command('update_statistics')


def start():
    # Only start in the main process (avoid autoreloader double-start)
    if os.environ.get('RUN_MAIN') != 'true':
        return

    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), 'default')

    scheduler.add_job(
        backup_website_job,
        trigger='cron',
        hour='23',
        minute='59',
        id='backup_website_job',
        replace_existing=True,
    )

    scheduler.add_job(
        update_statistics_job,
        trigger='cron',
        minute='*',
        id='update_statistics_job',
        replace_existing=True,
    )

    scheduler.start()
    logger.info('Scheduler started!')
