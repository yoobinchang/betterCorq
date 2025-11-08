# load event data, matching algorithm that suggests events based on user's free time
import json
from datetime import datetime
from utils.time_utils import calculate_free_time, is_within_tolerance

EVENTS_PATH = "backend/data/events_est.json"
SCHEDULE_PATH = "backend/data/schedule.json"

def load_events():
    """Load all campus events"""
    with open(EVENTS_PATH, "r") as f:
        return json.load(f)


def recommend_events(events, schedule_data, selected_days, tolerance):
    """
    Recommend events that fit within user's free time,
    using user-defined tolerance (in minutes).
    """
    free_times = calculate_free_time(schedule_data)
    recommended = []

    for e in events:
        day = e["day"]
        if day not in selected_days:
            continue  # skip unselected days

        for free_start, free_end in free_times.get(day, []):
            if is_within_tolerance(e["start"], free_start, free_end, tolerance):
                recommended.append(e)
                break

    return recommended

    # Simple matching algorithm: recommend events that don’t overlap
    recommended = []
    for event in events:
        event_day = event.get("day")
        event_start = datetime.strptime(event["start"], "%Y-%m-%d %H:%M:%S")
        event_end = datetime.strptime(event["end"], "%Y-%m-%d %H:%M:%S")

        conflict = False
        for busy in busy_times:
            if busy["day"] == event_day:
                busy_start = datetime.strptime(busy["start"], "%H:%M")
                busy_end = datetime.strptime(busy["end"], "%H:%M")

                # Check time overlap
                if busy_start <= event_start.time() <= busy_end or busy_start <= event_end.time() <= busy_end:
                    conflict = True
                    break

        if not conflict:
            recommended.append(event)

    return recommended
