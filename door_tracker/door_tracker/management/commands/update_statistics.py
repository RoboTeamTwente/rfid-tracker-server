from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Avg, Sum
from django.utils import timezone

from webui.models import Log, Statistics


class Command(BaseCommand):
    help = 'Update statistics for all users'

    def minutes_today(self, user):
        today = timezone.localdate()
        now = timezone.localtime()
        minutes_worked = 0

        logs = (
            Log.objects.filter(
                tag__owner=user,
                time__date=today,
            )
            .select_related('tag')
            .order_by('time')
        )

        checkin_time = None
        first_log = True

        for log in logs:
            if log.type == Log.LogEntryType.CHECKIN:
                checkin_time = log.time
                first_log = False
            elif log.type == Log.LogEntryType.CHECKOUT:
                if checkin_time and not first_log:
                    delta = timezone.localtime(log.time) - timezone.localtime(
                        checkin_time
                    )
                    minutes_worked += int(delta.total_seconds() // 60)
                    checkin_time = None
                elif first_log:
                    midnight = timezone.make_aware(
                        timezone.datetime.combine(
                            timezone.localdate(log.time),
                            timezone.datetime.min.time(),
                        )
                    )
                    delta = timezone.localtime(log.time) - midnight
                    minutes_worked += int(delta.total_seconds() // 60)
                    first_log = False

        if checkin_time:
            delta = now - timezone.localtime(checkin_time)
            minutes_worked += int(delta.total_seconds() // 60)

        return minutes_worked

    def minutes_week(self, user):
        today = timezone.localdate()
        start_of_week = today - timezone.timedelta(days=today.weekday())

        total_week = (
            Statistics.objects.filter(
                person=user,
                date__date__gte=start_of_week,
                date__date__lte=today,
            ).aggregate(total=Sum('minutes_day'))['total']
            or 0
        )

        return total_week

    def minutes_month(self, user):
        today = timezone.localdate()
        start_of_month = today.replace(day=1)

        total_month = (
            Statistics.objects.filter(
                person=user,
                date__date__gte=start_of_month,
                date__date__lte=today,
            ).aggregate(total=Sum('minutes_day'))['total']
            or 0
        )

        return total_month

    def handle(self, *args, **options):
        now = timezone.localtime()
        today_date = now.date()

        for user in User.objects.all():
            # Compute minutes
            minutes_day_val = self.minutes_today(user)
            minutes_week_val = self.minutes_week(user)
            minutes_month_val = self.minutes_month(user)

            # Update or create statistics for today
            stats, created = Statistics.objects.update_or_create(
                person=user,
                date__date=today_date,
                defaults={
                    'minutes_day': minutes_day_val,
                    'minutes_week': minutes_week_val,
                    'minutes_month': minutes_month_val,
                    'average_week': 0,
                    'total_minutes': 0,
                    'date': now,
                },
            )

            # Aggregate for averages
            agg = Statistics.objects.filter(person=user).aggregate(
                average_week=Avg('minutes_week'),
                total_minutes=Sum('minutes_day'),
            )

            stats.average_week = agg['average_week'] or 0
            stats.total_minutes = agg['total_minutes'] or 0
            stats.save(
                update_fields=[
                    'minutes_day',
                    'minutes_week',
                    'minutes_month',
                    'average_week',
                    'total_minutes',
                ]
            )

            self.stdout.write(
                f'Updated statistics for {user.username}: '
                f'Day={minutes_day_val}, Week={minutes_week_val}, Month={minutes_month_val}'
            )

        self.stdout.write(
            self.style.SUCCESS('Successfully updated statistics for all users.')
        )
