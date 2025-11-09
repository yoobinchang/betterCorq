# backend/services/schedule_service.py

import json
import os
from datetime import datetime
from services.event_service import fetch_events_from_corq, filter_events_by_free_time

# === File path ===
SCHEDULE_PATH = "backend/data/schedule.json"
FREE_TIME_PATH = "backend/data/free_time.json"
MATCHED_PATH = "backend/data/matched_events.json"


# === Load & Save ===
def load_schedule():
    if not os.path.exists(SCHEDULE_PATH):
        return {"message": "No schedule found yet."}
    with open(SCHEDULE_PATH, "r") as f:
        return json.load(f)

def save_json(path, data):
    """Generic JSON save utility"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# === Utility ===
def str_to_time(s):
    return datetime.strptime(s, "%H:%M").time()


# === Core: busy → free ===
def calc_free_time(busy_schedule, start="08:00", end="22:00"):
    """
    Convert BUSY schedule (class times) into FREE time schedule.
    Input example:
      {'Mon': [['09:30','10:50'], ['14:00','14:55']], 'Tue': [['12:30','13:45']]}
    Output example:
      {'Mon': [['08:00','09:30'], ['10:50','14:00'], ['14:55','22:00']], ...}
    """
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


# === NEW: Calculate Free Time Only (no save, for preview) ===
def calc_free_time_only(busy_schedule):
    """
    Used for AI upload route — only calculates free time without saving anything.
    """
    return calc_free_time(busy_schedule)


# === Existing: Full pipeline (AI → save → fetch events → match) ===
def generate_free_time():
    """Used only when finalizing user free time"""
    print("🚀 Generating free time and matching events...")

    busy_schedule = load_schedule()
    if "message" in busy_schedule:
        print("❌ No busy schedule found.")
        return {"message": "No busy schedule to process."}

    free_time = calc_free_time(busy_schedule)
    save_json(FREE_TIME_PATH, free_time)
    print("🕓 Free time saved.")

    latest_events = fetch_events_from_corq()
    matched_events = filter_events_by_free_time(events=latest_events, free_time=free_time)

    save_json(MATCHED_PATH, matched_events)
    print(f"✅ {len(matched_events)} matched events saved → {MATCHED_PATH}")

    return {
        "free_time": free_time,
        "matched_events_count": len(matched_events),
        "matched_events": matched_events
    }

# === Save user's manually selected free time ===
def save_user_free_time(data):
    """
    Save the user's selected/adjusted free time schedule
    (from frontend 'Save' button).
    """
    try:
        os.makedirs(os.path.dirname(FREE_TIME_PATH), exist_ok=True)
        with open(FREE_TIME_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"💾 Saved user free time → {FREE_TIME_PATH}")
        return {"message": "✅ Free time saved successfully."}

    except Exception as e:
        print(f"❌ Failed to save user free time: {e}")
        return {"error": str(e)}

def generate_matched_events():
    """
    Wrapper for backward compatibility with routes that import this name.
    Simply calls generate_free_time().
    """
    return generate_free_time()
