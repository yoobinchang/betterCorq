# load schedule data created by AI, user save schedule
import json
import os

SCHEDULE_PATH = "backend/data/schedule.json"

def load_schedule():
    """Read and return the saved schedule data"""
    if not os.path.exists(SCHEDULE_PATH):
        return {"message": "No schedule found yet."}

    with open(SCHEDULE_PATH, "r") as f:
        return json.load(f)

def save_schedule(data):
    """Save updated schedule (after user edits)"""
    with open(SCHEDULE_PATH, "w") as f:
        json.dump(data, f, indent=2)
