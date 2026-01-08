from datetime import datetime, timezone, timedelta

# IST timezone offset (UTC+5:30)
IST_OFFSET = timedelta(hours=5, minutes=30)


def to_ist(dt: datetime | None) -> datetime | None:
    """Convert UTC datetime to IST (Indian Standard Time - UTC+5:30)"""
    if dt is None:
        return None

    # If datetime is naive (no timezone info), assume it's UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    # Convert to IST
    ist_tz = timezone(IST_OFFSET)
    return dt.astimezone(ist_tz)


def to_ist_string(dt: datetime | None) -> str | None:
    """Convert UTC datetime to IST and return as ISO format string"""
    if dt is None:
        return None

    ist_dt = to_ist(dt)
    return ist_dt.isoformat() if ist_dt else None
