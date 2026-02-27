from datetime import datetime, time, timedelta

import pytz
from django.db.models import (
    Case,
    DurationField,
    ExpressionWrapper,
    F,
    Q,
    Sum,
    When,
)
from django.db.models.functions import Coalesce, ExtractWeek, ExtractYear
from django.utils import timezone
from pytz import AmbiguousTimeError, NonExistentTimeError

from .models import Assignment, Session

# Explicitly define Amsterdam Timezone
AMSTERDAM_TZ = pytz.timezone('Europe/Amsterdam')


def get_sessions_time(user, start_of_day, end_of_day):
    # Ensure inputs are aware to avoid DB warnings/errors
    if timezone.is_naive(start_of_day) or timezone.is_naive(end_of_day):
        raise ValueError('get_sessions_time expects aware datetimes')

    # Get all sessions that overlap with the specified range
    sessions = Session.objects.filter(
        Q(checkin__time__lte=end_of_day),
        Q(checkout__time__gte=start_of_day) | Q(checkout__time__isnull=True),
        user=user,
    )

    # Replace null with current time for ongoing sessions
    # Note: timezone.now() is UTC. The comparison logic below handles the clamping.
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
    # Convert dates to Amsterdam boundaries first
    start_dt = AMSTERDAM_TZ.localize(datetime.combine(start_day, time.min))
    # End day should be the *end* of that day, or start of next
    end_dt = AMSTERDAM_TZ.localize(
        datetime.combine(end_day + timedelta(days=1), time.max)
    )

    assignments = list(
        Assignment.objects.filter(user=user, starting_from__lte=end_dt).order_by(
            'starting_from'
        )
    )

    # Filter Python-side to ensure logic consistency
    previous_assignments = [a for a in assignments if a.starting_from <= start_dt]
    current_assignments = [a for a in assignments if a.starting_from > start_dt]

    if previous_assignments:
        previous_assignment = previous_assignments[-1]
        assignments = [previous_assignment] + current_assignments
    else:
        assignments = current_assignments

    quota_durations = []

    for i, assignment in enumerate(assignments):
        # FIX: Use the actual overlap start, not the global start_day
        # We ensure the assignment starting_from is compared correctly (aware vs aware)
        period_start = max(assignment.starting_from, start_dt)

        if i < len(assignments) - 1:
            period_end = assignments[i + 1].starting_from
        else:
            period_end = end_dt

        # Calculate duration
        # We use total_seconds because subtraction might return timedelta
        duration_days = (period_end - period_start).total_seconds() / 86400

        # Optional: Rounding logic depending on business rule (e.g., partial days)
        quota_durations.append(
            {'quota': assignment.quota, 'duration_days': duration_days}
        )
    return quota_durations


def get_minutes_today(user, day):
    # 'day' is expected to be a date object or datetime
    if isinstance(day, datetime):
        day = day.date()

    # Create boundary in Amsterdam time
    start_of_day_ams = AMSTERDAM_TZ.localize(datetime.combine(day, time.min))

    # End of day is start of next day (easier for calculations than max time)
    end_of_day_ams = AMSTERDAM_TZ.localize(
        datetime.combine(day + timedelta(days=1), time.min)
    ) - timedelta(microseconds=1)

    return get_sessions_time(user, start_of_day_ams, end_of_day_ams)


def get_minutes_this_week(user, day):
    # 1. Normalize input to Amsterdam Date
    if isinstance(day, datetime):
        # Convert to Amsterdam to ensure we find the correct "Monday"
        # If it's Monday 00:30 UTC, it's Monday 02:30 NL.
        # But if it's Sunday 23:30 UTC, it's Monday 01:30 NL.
        if timezone.is_naive(day):
            # Fallback if naive (assume system time), usually better to raise error
            day = AMSTERDAM_TZ.localize(day)
        else:
            day = day.astimezone(AMSTERDAM_TZ)
        current_date_ams = day.date()
    else:
        current_date_ams = day

    # 2. Find start of week (Monday) based on Amsterdam Date
    start_of_week_date = current_date_ams - timedelta(days=current_date_ams.weekday())

    # 3. Create Aware Boundaries
    start_of_week_ams = AMSTERDAM_TZ.localize(
        datetime.combine(start_of_week_date, time.min)
    )
    end_of_week_ams = start_of_week_ams + timedelta(days=7) - timedelta(microseconds=1)

    return get_sessions_time(user, start_of_week_ams, end_of_week_ams)


def get_minutes_this_month(user, day):
    if isinstance(day, datetime):
        # Convert to Amsterdam to find correct Month
        if timezone.is_naive(day):
            day = AMSTERDAM_TZ.localize(day)
        else:
            day = day.astimezone(AMSTERDAM_TZ)
        day = day.date()

    # Start of month
    start_of_month_date = day.replace(day=1)

    # End of month calculation
    if day.month == 12:
        next_month_date = day.replace(year=day.year + 1, month=1, day=1)
    else:
        next_month_date = day.replace(month=day.month + 1, day=1)

    start_of_month_ams = AMSTERDAM_TZ.localize(
        datetime.combine(start_of_month_date, time.min)
    )
    end_of_month_ams = AMSTERDAM_TZ.localize(
        datetime.combine(next_month_date, time.min)
    ) - timedelta(microseconds=1)

    return get_sessions_time(user, start_of_month_ams, end_of_month_ams)


def get_total_minutes(user, day):
    # Get the date of the earliest checkin
    earliest_session = (
        Session.objects.filter(user=user, checkin__isnull=False)
        .order_by('checkin__time')
        .first()
    )

    if earliest_session is None or not hasattr(earliest_session, 'checkin'):
        return 0  # No checkin yet

    # Earliest session is already Aware (UTC from DB).
    # We should use it directly or floor it to the day start in Amsterdam.
    earliest_checkin_ams = earliest_session.checkin.time.astimezone(AMSTERDAM_TZ)
    start_of_period = earliest_checkin_ams.replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    # Handle 'day' argument (End of period)
    if isinstance(day, datetime):
        if timezone.is_naive(day):
            day = AMSTERDAM_TZ.localize(day)
        else:
            day = day.astimezone(AMSTERDAM_TZ)
        end_date = day.date()
    else:
        end_date = day

    end_of_period = AMSTERDAM_TZ.localize(
        datetime.combine(end_date + timedelta(days=1), time.min)
    ) - timedelta(microseconds=1)

    return get_sessions_time(user, start_of_period, end_of_period)


def get_average_week(user, day):
    total_minutes = get_total_minutes(user, day)

    if total_minutes == 0:
        return 0

    # Count distinct weeks with at least one check-in
    active_weeks_count = (
        Session.objects.filter(user=user, checkin__isnull=False)
        .annotate(
            year=ExtractYear('checkin__time', tzinfo=AMSTERDAM_TZ),
            week=ExtractWeek('checkin__time', tzinfo=AMSTERDAM_TZ),
        )
        .values('year', 'week')
        .distinct()
        .count()
    )

    if active_weeks_count == 0:
        return total_minutes

    return int(total_minutes // active_weeks_count)


# Helper function kept for compatibility, but usage replaced with explicit AMSTERDAM_TZ
def safe_make_aware(dt):
    if dt is None:
        return None
    if timezone.is_naive(dt):
        try:
            return timezone.make_aware(dt, AMSTERDAM_TZ)
        except (AmbiguousTimeError, NonExistentTimeError):
            return AMSTERDAM_TZ.localize(dt)
    return dt
