from datetime import datetime, timedelta

from django.db.models import (
    Case,
    DurationField,
    ExpressionWrapper,
    F,
    Q,
    Sum,
    When,
)
from django.db.models.functions import Coalesce
from django.http import JsonResponse as JSONResponse
from django.shortcuts import render
from django.utils import timezone

from midas.models import Session


def dashboard(request):
    return render(request, 'midas/index.html')


def get_statistics(request):
    today = timezone.now().date()

    minutes_today = get_minutes_today(request, today)
    minutes_this_week = get_minutes_this_week(request, today)
    minutes_this_month = get_minutes_this_month(request, today)
    total_minutes = get_total_minutes(request, today)
    average_week = get_average_week(request, today, total_minutes)

    return JSONResponse(
        {
            'minutes_today': minutes_today,
            'minutes_this_week': minutes_this_week,
            'minutes_this_month': minutes_this_month,
            'average_week': average_week,
            'total_minutes': total_minutes,
        }
    )


def get_sessions_time(request, start_of_day, end_of_day):
    # Get all sessions that overlap with the specified range
    sessions = Session.objects.filter(
        Q(checkin__time__lte=end_of_day),
        Q(checkout__time__gte=start_of_day) | Q(checkout__time__isnull=True),
        user=request.user,
    )

    # Replace null with current time for ongoing sessions
    sessions = sessions.annotate(
        checkout_time=Coalesce('checkout__time', timezone.now())
    )

    # Clamp checkin and checkout times to the specified range
    sessions = sessions.annotate(
        clamped_checkin=Case(
            When(checkin__time__lt=start_of_day, then=start_of_day),
            default=F('checkin__time'),
        ),
        clamped_checkout=Case(
            When(checkout_time__gt=end_of_day, then=end_of_day),
            default=F('checkout_time'),
        ),
    )

    # Compute duration and sum
    sessions = sessions.annotate(
        duration=ExpressionWrapper(
            F('clamped_checkout') - F('clamped_checkin'), output_field=DurationField()
        )
    )

    total_duration = sessions.aggregate(total=Sum('duration'))['total']

    if total_duration is None:
        return 0

    return int(total_duration.total_seconds() // 60)


def get_minutes_today(request, day):
    # Get start and end of the day
    start_of_day = datetime.combine(
        day, datetime.min.time(), tzinfo=timezone.get_current_timezone()
    )
    end_of_day = datetime.combine(
        day, datetime.max.time(), tzinfo=timezone.get_current_timezone()
    )

    return get_sessions_time(request, start_of_day, end_of_day)


def get_minutes_this_week(request, day):
    # Get start and end of the week (Monday to Sunday)
    start_of_week = day - timezone.timedelta(days=day.weekday())
    start_of_day = datetime.combine(
        start_of_week, datetime.min.time(), tzinfo=timezone.get_current_timezone()
    )
    end_of_week = start_of_week + timezone.timedelta(days=6)
    end_of_day = datetime.combine(
        end_of_week, datetime.max.time(), tzinfo=timezone.get_current_timezone()
    )

    return get_sessions_time(request, start_of_day, end_of_day)


def get_minutes_this_month(request, day):
    # Get start and end of the month
    start_of_month = day.replace(day=1)
    start_of_day = datetime.combine(
        start_of_month, datetime.min.time(), tzinfo=timezone.get_current_timezone()
    )
    # Calculate the last day of the month
    if day.month == 12:
        end_of_month = day.replace(year=day.year + 1, month=1, day=1) - timedelta(
            days=1
        )
    else:
        end_of_month = day.replace(month=day.month + 1, day=1) - timedelta(days=1)
    end_of_day = datetime.combine(
        end_of_month, datetime.max.time(), tzinfo=timezone.get_current_timezone()
    )

    return get_sessions_time(request, start_of_day, end_of_day)


def get_total_minutes(request, day):
    # Get the date of the earliest checkin
    earliest_session = (
        Session.objects.filter(user=request.user, checkin__isnull=False)
        .order_by('checkin__time')
        .first()
    )

    if earliest_session is None or not hasattr(earliest_session, 'checkin'):
        print('No checkin yet')
        return 0  # No checkin yet

    latest_session = day

    start_of_day = datetime.combine(
        earliest_session.checkin.time.date(),
        datetime.min.time(),
        tzinfo=timezone.get_current_timezone(),
    )
    end_of_day = datetime.combine(
        latest_session, datetime.max.time(), tzinfo=timezone.get_current_timezone()
    )

    return get_sessions_time(request, start_of_day, end_of_day)


def get_average_week(request, day, total_minutes):
    # Get the date of the earliest checkin
    earliest_session = (
        Session.objects.filter(user=request.user, checkin__isnull=False)
        .order_by('checkin__time')
        .first()
    )

    if earliest_session is None or not hasattr(earliest_session, 'checkin'):
        print('No checkin yet')
        return 0  # No checkin yet

    first_checkin_date = earliest_session.checkin.time.date()
    # Calculate the number of weeks between the first checkin and the given day
    days_difference = (
        day - first_checkin_date
    ).days + 1  # +1 to include the current day
    weeks_difference = days_difference / 7

    if weeks_difference == 0:
        return total_minutes  # Avoid division by zero, return total minutes as average

    return int(total_minutes // weeks_difference)
