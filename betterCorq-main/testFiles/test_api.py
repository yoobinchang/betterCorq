import requests
import json
from datetime import datetime
import pytz

# API settings
url = "https://stonybrook.campuslabs.com/engage/api/discovery/event/search?endsAfter=2025-11-06T00:00:00Z&take=200&sort=startsOn&order=ascending"

headers = {
    "accept": "application/json",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "referer": "https://stonybrook.campuslabs.com/engage/"
}

# Timezone config
utc = pytz.utc
eastern = pytz.timezone("US/Eastern")

# Fetch data from API
res = requests.get(url, headers=headers)
print("Status code:", res.status_code)

if res.status_code == 200:
    data = res.json()
    events = data.get("value", [])
    print(f"✅ {len(events)} events fetched")

    converted_events = []

    for e in events:
        start_utc = e.get("startsOn")
        end_utc = e.get("endsOn")

        # convert time to EST
        if start_utc and end_utc:
            start_dt = datetime.fromisoformat(start_utc.replace("Z", "+00:00")).astimezone(eastern)
            end_dt = datetime.fromisoformat(end_utc.replace("Z", "+00:00")).astimezone(eastern)
            start_est = start_dt.strftime("%Y-%m-%d %I:%M %p %Z")
            end_est = end_dt.strftime("%I:%M %p %Z")
        else:
            start_est, end_est = None, None

        converted_events.append({
            "name": e.get("name"),
            "start": start_est,
            "end": end_est,
            "location": e.get("location"),
            "organization": e.get("organizationName"),
        })

    # Save to JSON file
    with open("events_est.json", "w", encoding="utf-8") as f:
        json.dump(converted_events, f, ensure_ascii=False, indent=2)

    # Print sample output
    print("\n🎬 Sample events (converted to EST):\n")
    for i, e in enumerate(converted_events[:5], start=1):
        print(f"{i}. 🎉 {e['name']}")
        print(f"   📅 {e['start']} → {e['end']}")
        print(f"   📍 {e['location']}")
        print(f"   🏫 {e['organization']}")
        print("-" * 60)

else:
    print("❌ Failed to fetch data:", res.status_code)
