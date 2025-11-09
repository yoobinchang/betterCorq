import json
import os
import requests
from datetime import datetime, timedelta
import pytz

EVENTS_PATH = "backend/data/events_est.json"

def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def str_to_time(s):
    return datetime.strptime(s, "%H:%M").time()

# === Fetch latest CORQ events ===
def fetch_events_from_corq():
    """Fetch current events from CORQ (Stony Brook Engage API) and save locally."""
    url = "https://stonybrook.campuslabs.com/engage/api/discovery/event/search?endsAfter=2025-11-06T00:00:00Z&take=200&sort=startsOn&order=ascending"
    headers = {
        "accept": "application/json",
        "user-agent": "Mozilla/5.0",
        "referer": "https://stonybrook.campuslabs.com/engage/"
    }
    eastern = pytz.timezone("US/Eastern")

    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print(f"❌ Failed to fetch data: {res.status_code}")
            return []

        data = res.json()
        events = data.get("value", [])
        print(f"✅ {len(events)} events fetched from CORQ")

        converted = []
        for e in events:
            start_utc = e.get("startsOn")
            end_utc = e.get("endsOn")

            if not start_utc or not end_utc:
                continue

            start_dt = datetime.fromisoformat(start_utc.replace("Z", "+00:00")).astimezone(eastern)
            end_dt = datetime.fromisoformat(end_utc.replace("Z", "+00:00")).astimezone(eastern)

            converted.append({
                "name": e.get("name"),
                "start": start_dt.strftime("%Y-%m-%d %I:%M %p EST"),
                "end": end_dt.strftime("%I:%M %p EST"),
                "location": e.get("location"),
                "organization": e.get("organizationName")
            })

        with open(EVENTS_PATH, "w", encoding="utf-8") as f:
            json.dump(converted, f, ensure_ascii=False, indent=2)

        print(f"💾 Saved {len(converted)} events → {EVENTS_PATH}")
        return converted

    except Exception as e:
        print(f"⚠️ Error while fetching events: {e}")
        return []

# === Filter events based on Free Time ===
def filter_events_by_free_time(events, free_time):
    """Return events that fit into user's free time during the next 7 days."""
    est = pytz.timezone("US/Eastern")
    now = datetime.now(est)
    end_range = (now + timedelta(days=7)).replace(hour=22, minute=0, second=0, microsecond=0)

    matched = []
    weekday_map = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    for e in events:
        start_str = e.get("start")
        end_str = e.get("end")

        try:
            start_dt = datetime.strptime(start_str, "%Y-%m-%d %I:%M %p EST")
            end_dt = datetime.strptime(end_str, "%I:%M %p EST")
            end_dt = start_dt.replace(hour=end_dt.hour, minute=end_dt.minute)
        except Exception:
            continue

        if not (now <= start_dt <= end_range):
            continue

        weekday = weekday_map[start_dt.weekday()]
        event_start, event_end = start_dt.time(), end_dt.time()

        for interval in free_time.get(weekday, []):
            free_start, free_end = str_to_time(interval[0]), str_to_time(interval[1])
            if free_start <= event_start and event_end <= free_end:
                matched.append(e)
                break

    print(f"✅ Found {len(matched)} available events.")
    return matched
