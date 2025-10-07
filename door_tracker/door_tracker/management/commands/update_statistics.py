from datetime import datetime, timedelta

import pytz
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Avg, F, Sum
from django.utils import timezone
from webui.models import Log, Statistics


class Command(BaseCommand):
    help = 'Update statistics for all users'

    def minutes_for_day(self, user, day):
        today = timezone.localdate()

        # Get all the logs from a user in a day ordered by time
        logs = (
            Log.objects.filter(
                tag__owner=user,
                time__date=day,
                type__in=[Log.LogEntryType.CHECKIN, Log.LogEntryType.CHECKOUT],
            )
            .select_related('tag')
            .order_by('time')
        )
        logs_list = list(logs)

        if not logs.exists():
            return 0

        # If the the first log is checkout count as if checkin at 00:00, if the last log is checkin coint as if checkout at 23:59
        beginning = timezone.make_aware(datetime.combine(day, datetime.min.time()))
        if day == today:
            end = timezone.localtime()
        else:
            end = timezone.make_aware(datetime.combine(day, datetime.max.time()))

        if logs_list[0].type == Log.LogEntryType.CHECKOUT:
            logs_list.insert(0, Log(type=Log.LogEntryType.CHECKIN, time=beginning))
        if logs_list[-1].type == Log.LogEntryType.CHECKIN:
            logs_list.append(Log(type=Log.LogEntryType.CHECKOUT, time=end))

        # Calculate minutes between checkins and checkouts
        minutes_worked = 0
        checkin_time = None

        for log in logs_list:
            log_UTC2 = log.time.astimezone(pytz.timezone('Etc/GMT-2'))
            if log.type == Log.LogEntryType.CHECKIN:
                checkin_time = log_UTC2

            if log.type == Log.LogEntryType.CHECKOUT:
                minutes_worked += (log_UTC2 - checkin_time).total_seconds() // 60
                checkin_time = None

        return minutes_worked

    def minutes_week_up_to(self, user, day):
        # Calculate total minutes for the week ending on 'day'
        start_of_week = day - timedelta(days=day.weekday())
        total = 0

        for i in range((day - start_of_week).days + 1):
            d = start_of_week + timedelta(days=i)
            total += self.minutes_for_day(user, d)

        return total

    def minutes_month_up_to(self, user, day):
        # Calculate total minutes for the month ending on 'day'
        start_of_month = day.replace(day=1)
        total = 0

        for i in range((day - start_of_month).days + 1):
            d = start_of_month + timedelta(days=i)
            total += self.minutes_for_day(user, d)

        return total

    def handle(self, *args, **options):
        now = timezone.localtime()
        today = now.date()
        start_of_month = today.replace(day=1)

        # Loop through every day of the current month up to today
        for single_date in (
            start_of_month + timedelta(days=n)
            for n in range((today - start_of_month).days + 1)
        ):
            if single_date == today:
                stat_date = now
            else:
                stat_date = timezone.make_aware(
                    datetime.combine(single_date, datetime.min.time())
                )

            # Loop though all users
            for user in User.objects.all():
                minutes_day_val = self.minutes_for_day(user, single_date)
                minutes_week_val = 0
                minutes_month_val = 0
                minutes_week_val = self.minutes_week_up_to(user, single_date)
                minutes_month_val = self.minutes_month_up_to(user, single_date)

                stats, created = Statistics.objects.update_or_create(
                    person=user,
                    date__date=single_date,
                    defaults={
                        'minutes_day': minutes_day_val,
                        'minutes_week': minutes_week_val,
                        'minutes_month': minutes_month_val,
                        'average_week': 0,
                        'total_minutes': 0,
                        'date': stat_date,
                    },
                )

                # Aggregate for averages
                agg = Statistics.objects.filter(
                    person=user, date__lte=stat_date
                ).aggregate(
                    average_week=Avg(F('minutes_day') * 7),
                    total_minutes=Sum('minutes_day'),
                )

                stats.average_week = agg['average_week'] or 0
                stats.total_minutes = agg['total_minutes'] or 0
                stats.save()

        self.stdout.write(
            self.style.SUCCESS(
                'Successfully updated statistics for all users for the current month.'
            )
        )
