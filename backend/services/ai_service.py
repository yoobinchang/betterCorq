# extract busy time & free time data by analyzing schedule image with Gemini API
import base64
import requests
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def extract_schedule_from_image(file):
    """
    Sends schedule image to OpenRouter (Gemini Vision or Llama 3.2 Vision)
    and parses AI response into structured JSON.
    """

    # Convert uploaded file → base64 string
    img_bytes = file.read()
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")

    # Define API request payload
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "google/gemini-2.5-pro",  # or "meta-llama/llama-3.2-90b-vision-instruct"
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract all class names, start/end times, and days from this schedule image in JSON format. Use 24-hour time."},
                    {"type": "image", "image_base64": img_base64}
                ]
            }
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions",
                             headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"API error: {response.text}")

    # Parse model response
    data = response.json()
    ai_text = data["choices"][0]["message"]["content"]

    # Save schedule to file
    with open("backend/data/schedule.json", "w") as f:
        f.write(ai_text)

    return ai_text
