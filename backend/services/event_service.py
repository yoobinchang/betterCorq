# load event data, matching algorithm that suggests events based on user's free time
import json
from datetime import datetime

EVENTS_PATH = "backend/data/events_est.json"
SCHEDULE_PATH = "backend/data/schedule.json"

def load_events():
    """Load all campus events"""
    with open(EVENTS_PATH, "r") as f:
        return json.load(f)


def recommend_events():
    """
    Compare user's free time (from schedule.json)
    with campus events, and return events that fit.
    """
    try:
        with open(SCHEDULE_PATH, "r") as f:
            schedule = json.load(f)
    except FileNotFoundError:
        return {"error": "No schedule found."}

    with open(EVENTS_PATH, "r") as f:
        events = json.load(f)

    # Extract busy time ranges
    busy_times = []
    for cls in schedule.get("classes", []):
        busy_times.append({
            "day": cls["day"],
            "start": cls["start"],
            "end": cls["end"]
        })

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
