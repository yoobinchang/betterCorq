# backend/utils/time_utils.py
# ---------------------------------------------------
# Utility functions for time processing and schedule analysis.
# Calculates free time from a user's class schedule,
# converts time formats, and applies matching tolerance.
# ---------------------------------------------------

from datetime import datetime, timedelta

def calculate_free_time(schedule_data):
    """Same as before — calculates free blocks per day."""
    day_hours = (8 * 60, 22 * 60)
    free_times = {}

    for day, busy_blocks in schedule_data.items():
        busy_sorted = sorted(busy_blocks, key=lambda x: x[0])
        free_blocks = []
        start = day_hours[0]

        for start_busy, end_busy in busy_sorted:
            busy_start_min = int(start_busy[:2]) * 60 + int(start_busy[3:])
            busy_end_min = int(end_busy[:2]) * 60 + int(end_busy[3:])
            if busy_start_min > start:
                free_blocks.append((
                    f"{start // 60:02d}:{start % 60:02d}",
                    f"{busy_start_min // 60:02d}:{busy_start_min % 60:02d}"
                ))
            start = max(start, busy_end_min)

        if start < day_hours[1]:
            free_blocks.append((
                f"{start // 60:02d}:{start % 60:02d}",
                f"{day_hours[1] // 60:02d}:{day_hours[1] % 60:02d}"
            ))

        free_times[day] = free_blocks

    return free_times


def to_iso_format(date_str, time_str):
    """Convert 'YYYY-MM-DD' + 'HH:MM' to ISO 8601 format."""
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    return dt.strftime("%Y%m%d%H%M")


def is_within_tolerance(event_time, free_start, free_end, tolerance):
    """
    Check whether an event fits within the user's free time block,
    allowing ±tolerance (user-defined minutes).

    Args:
        event_time (str): Event start time, e.g. "13:05"
        free_start (str): Start of free block, e.g. "13:00"
        free_end (str): End of free block, e.g. "14:00"
        tolerance (int): Number of minutes set by user

    Returns:
        bool: True if event fits within the adjusted window
    """
    t_event = datetime.strptime(event_time, "%H:%M")
    t_start = datetime.strptime(free_start, "%H:%M") - timedelta(minutes=tolerance)
    t_end = datetime.strptime(free_end, "%H:%M") + timedelta(minutes=tolerance)
    return t_start <= t_event <= t_end
