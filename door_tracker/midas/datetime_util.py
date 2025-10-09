from datetime import datetime, timedelta


def to_start_of_day(dt: datetime):
    """Return midnight of the same date."""
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def to_end_of_day(dt: datetime):
    """Return 23:59:59.9999999 of the same date."""
    return to_start_of_day(dt) + timedelta(days=1, microseconds=-1)


def to_start_of_week(dt: datetime):
    """Return start of the same week."""
    dt = to_start_of_day(dt)
    dt -= timedelta(days=dt.weekday())
    return dt


def to_end_of_week(start: datetime):
    """Return end of the same week."""
    start = to_start_of_week(start)
    return start + timedelta(days=7, microseconds=-1)


def to_start_of_month(dt: datetime):
    """Return start of the same month."""
    return to_start_of_day(dt).replace(day=1)


def to_end_of_month(dt: datetime):
    """Return end of the same month."""
    dt = to_start_of_month(dt)
    dt.month += 1
    dt.day -= 1
    return to_end_of_day(dt)
