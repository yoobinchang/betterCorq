# backend/services/schedule_service.py

import json
import os
from datetime import datetime

# === File path ===
SCHEDULE_PATH = "backend/data/schedule.json"
FREE_TIME_PATH = "backend/data/free_time.json"

# === Load & Save ===
def load_schedule():
    """Read and return the saved busy schedule (AI output)"""
    if not os.path.exists(SCHEDULE_PATH):
        return {"message": "No schedule found yet."}
    with open(SCHEDULE_PATH, "r") as f:
        return json.load(f)

def save_schedule(data):
    """Save updated busy schedule (after user edits)"""
    with open(SCHEDULE_PATH, "w") as f:
        json.dump(data, f, indent=2)

# === Utility ===
def str_to_time(s):
    return datetime.strptime(s, "%H:%M").time()

# === Core logic: busy → free time ===
def calc_free_time(busy_schedule, start="08:00", end="22:00"):
    """Convert busy schedule dict into free schedule dict"""
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    free_schedule = {}
    day_start = str_to_time(start)
    day_end = str_to_time(end)

    for day in day_names:
        busy = busy_schedule.get(day, [])
        busy_sorted = sorted(busy, key=lambda x: x[0])
        free = []
        current = day_start

        for interval in busy_sorted:
            start_t, end_t = str_to_time(interval[0]), str_to_time(interval[1])
            if start_t > current:
                free.append([current.strftime("%H:%M"), start_t.strftime("%H:%M")])
            current = max(current, end_t)

        if current < day_end:
            free.append([current.strftime("%H:%M"), day_end.strftime("%H:%M")])

        free_schedule[day] = free

    return free_schedule

def generate_free_time():
    """Load busy schedule → calculate → save and return free time"""
    busy_schedule = load_schedule()

    if "message" in busy_schedule:  # schedule.json이 없는 경우
        return {"message": "No busy schedule to process."}

    free_time = calc_free_time(busy_schedule)

    with open(FREE_TIME_PATH, "w") as f:
        json.dump(free_time, f, indent=2)

    return free_time
