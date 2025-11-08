import requests
import base64
import json
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("❌ OPENROUTER_API_KEY not found in .env file")

MODEL = "google/gemini-2.5-pro"
IMAGE_PATH = "schedule.png"

# Convert image to base64
with open(IMAGE_PATH, "rb") as f:
    image_bytes = f.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

# Prompt
prompt = """
You are a schedule extraction assistant.

Analyze the uploaded timetable image and extract the student's schedule as structured JSON.

Each object should include:
- "day": day of the week (e.g., Monday, Tuesday)
- "start": start time in 12-hour format with AM/PM (e.g., "9:30AM")
- "end": end time in 12-hour format with AM/PM (e.g., "10:50AM")
- "course": course name and section (e.g., "CSE 113 - 01 Lecture")
- "location": building and room (e.g., "Humanities 1003")

If a course occurs on multiple days, output separate entries for each.
Output only valid JSON.
"""

# Send request
url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
}

data = {
    "model": MODEL,
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_base64", "image_base64": image_base64},
            ],
        }
    ],
}

res = requests.post(url, headers=headers, json=data)

if res.status_code == 200:
    result = res.json()
    output = result["choices"][0]["message"]["content"]
    print("✅ Extracted Schedule JSON:")
    print(output)

    with open("schedule.json", "w") as f:
        f.write(output)
    print("\n📁 Saved to schedule.json")
else:
    print(f"❌ Error {res.status_code}: {res.text}")
