from datetime import datetime, time, timedelta

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
from django.utils import timezone
from pytz import AmbiguousTimeError, NonExistentTimeError

from midas.models import Assignment, Session

# TODO: Get quota for that time period


def get_sessions_time(user, start_of_day, end_of_day):
    # Get all sessions that overlap with the specified range
    sessions = Session.objects.filter(
        Q(checkin__time__lte=end_of_day),
        Q(checkout__time__gte=start_of_day) | Q(checkout__time__isnull=True),
        user=user,
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
            F('clamped_checkout') - F('clamped_checkin'),
            output_field=DurationField(),
        )
    )

    total_duration = sessions.aggregate(total=Sum('duration'))['total']

    if total_duration is None:
        return 0

    return int(total_duration.total_seconds() // 60)


def get_quota_durations_time_period(user, start_day, end_day):
    start_day = timezone.make_aware(datetime.combine(start_day, time.min))
    end_day = timezone.make_aware(
        datetime.combine(end_day + timedelta(days=1), time.max)
    )

    assignments = list(
        Assignment.objects.filter(user=user, starting_from__lte=end_day).order_by(
            'starting_from'
        )
    )

    previous_assignments = [a for a in assignments if a.starting_from <= start_day]
    current_assignments = [a for a in assignments if a.starting_from > start_day]

    if previous_assignments:
        previous_assignment = previous_assignments[-1]
        assignments = [previous_assignment] + current_assignments
    else:
        assignments = current_assignments

    quota_durations = []

    for i, assignment in enumerate(assignments):
        period_start = max(assignment.starting_from, start_day)

        if i < len(assignments) - 1:
            period_end = assignments[i + 1].starting_from
        else:
            period_end = end_day

        duration_days = (period_end - period_start).days

        quota_durations.append(
            {'quota': assignment.quota, 'duration_days': duration_days}
        )

    return quota_durations


# def get_quotas_for_assignments(request, start_day, end_day):
#     aa = get_assignments_time_period(request, start_day, end_day)


def get_minutes_today(user, day):
    # Get start and end of the day
    start_of_day = safe_make_aware(datetime.combine(day, datetime.min.time()))

    # Using datetime.max will break it durin the time change (DST)
    # so we use the start of the next day minus 1 microsecond
    end_of_day = safe_make_aware(
        datetime.combine(day + timedelta(days=1), datetime.min.time())
    ) - timedelta(microseconds=1)

    return get_sessions_time(user, start_of_day, end_of_day)


def get_minutes_this_week(user, day):
    # Get start and end of the week (Monday to Sunday)
    start_of_week = day - timedelta(days=day.weekday())
    start_of_day = safe_make_aware(
        datetime.combine(
            start_of_week,
            datetime.min.time(),
        )
    )
    end_of_week = start_of_week + timedelta(days=6)

    # Using datetime.max will break it durin the time change (DST)
    # so we use the start of the next day minus 1 microsecond
    end_of_day = safe_make_aware(
        datetime.combine(end_of_week + timedelta(days=1), datetime.min.time()),
    ) - timedelta(microseconds=1)

    return get_sessions_time(user, start_of_day, end_of_day)


def get_minutes_this_month(user, day):
    # Get start and end of the month
    start_of_month = day.replace(day=1)
    start_of_day = safe_make_aware(
        datetime.combine(
            start_of_month,
            datetime.min.time(),
        )
    )
    # Calculate the last day of the month
    if day.month == 12:
        end_of_month = day.replace(year=day.year + 1, month=1, day=1) - timedelta(
            days=1
        )
    else:
        end_of_month = day.replace(month=day.month + 1, day=1) - timedelta(days=1)

    # Using datetime.max will break it durin the time change (DST)
    # so we use the start of the next day minus 1 microsecond
    end_of_day = safe_make_aware(
        datetime.combine(end_of_month + timedelta(days=1), datetime.min.time()),
    ) - timedelta(microseconds=1)

    return get_sessions_time(user, start_of_day, end_of_day)


def get_total_minutes(user, day):
    # Get the date of the earliest checkin
    earliest_session = (
        Session.objects.filter(user=user, checkin__isnull=False)
        .order_by('checkin__time')
        .first()
    )

    if earliest_session is None or not hasattr(earliest_session, 'checkin'):
        return 0  # No checkin yet

    latest_session = day

    start_of_day = safe_make_aware(
        datetime.combine(earliest_session.checkin.time.date(), datetime.min.time())
    )

    # Using datetime.max will break it durin the time change (DST)
    # so we use the start of the next day minus 1 microsecond
    end_of_day = safe_make_aware(
        datetime.combine(latest_session + timedelta(days=1), datetime.min.time()),
    ) - timedelta(microseconds=1)

    return get_sessions_time(user, start_of_day, end_of_day)


def get_average_week(user, day):
    total_minutes = get_total_minutes(user, day)
    # Get the date of the earliest checkin
    earliest_session = (
        Session.objects.filter(user=user, checkin__isnull=False)
        .order_by('checkin__time')
        .first()
    )

    if earliest_session is None or not hasattr(earliest_session, 'checkin'):
        return 0  # No checkin yet

    first_checkin_date = earliest_session.checkin.time

    # Calculate the number of weeks between the first checkin and the given day
    days_difference = (
        day - first_checkin_date
    ).days + 1  # +1 to include the current day
    weeks_difference = days_difference / 7

    if weeks_difference == 0:
        return total_minutes  # Avoid division by zero, return total minutes as average

    return int(total_minutes // weeks_difference)


def safe_make_aware(dt):
    # Make datetime aware (in django timezone)
    if dt is None:
        return None
    if timezone.is_naive(dt):
        try:
            return timezone.make_aware(dt, timezone.get_default_timezone())
        except (AmbiguousTimeError, NonExistentTimeError):
            # DST transition edge case: fallback to default behavior
            return timezone.get_default_timezone().localize(dt)
    return dt
