import base64
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def extract_schedule_from_image(file):
    """Send a schedule image to OpenRouter (GPT-4o) and get structured busy-time data."""
    print("📤 [AI Service] Starting image extraction process...")

    # === Convert image to base64 ===
    img_bytes = file.read()
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/yoobinchang/betterCorq",
        "User-Agent": "betterCorq/1.0 (https://github.com/yoobinchang)",
        "X-Title": "betterCorq AI Schedule Extractor"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "You are analyzing a weekly university schedule image. "
                            "Each green or colored block in the table represents one class (a busy period). "
                            "Your task is to extract only the busy times from each block.\n\n"
                            "INSTRUCTIONS:\n"
                            "1. For every visible class block, read the start and end time written inside it (e.g., '9:30AM - 10:50AM').\n"
                            "2. Identify which weekday column the block belongs to (Mon, Tue, Wed, Thu, or Fri).\n"
                            "3. Convert all 12-hour times with AM/PM into 24-hour format (HH:MM). Examples:\n"
                            "   - 9:30AM → 09:30\n"
                            "   - 10:50AM → 10:50\n"
                            "   - 3:30PM → 15:30\n"
                            "   - 4:50PM → 16:50\n"
                            "4. Output ONLY valid JSON, structured exactly like this:\n"
                            "{\n"
                            "  'Mon': [['09:30','10:50'], ['14:00','14:55']],\n"
                            "  'Tue': [['12:30','13:45']],\n"
                            "  'Wed': [],\n"
                            "  'Thu': [['09:30','10:50']],\n"
                            "  'Fri': []\n"
                            "}\n\n"
                            "RULES:\n"
                            "- Every block represents a busy time (class period). Collect all of them.\n"
                            "- Do NOT include text like course names or rooms, only time ranges.\n"
                            "- Do NOT guess; if a time is unreadable, skip that block.\n"
                            "- Ensure the output is strictly valid JSON and uses 24-hour time.\n"
                        )
                    },
                    {"type": "image", "image_base64": img_base64}
                ]
            }
        ]
    }

    print("🚀 Sending request to OpenRouter API...")

    # === Send request ===
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60
    )

    print(f"🔁 API responded with status {response.status_code}")

    # === Print partial response for debugging ===
    print("🔍 RAW RESPONSE START ===")
    print(response.text[:500])
    print("🔍 RAW RESPONSE END ===")

    # === Handle non-JSON or HTML errors ===
    if response.headers.get("Content-Type", "").startswith("text/html"):
        print("❌ OpenRouter returned HTML page (likely firewall block):")
        print(response.text[:300])
        raise Exception("403 HTML response: Firewall or Referer/User-Agent missing")

    # === Parse JSON safely ===
    try:
        data = response.json()
    except Exception:
        raise Exception(f"❌ Non-JSON response: {response.text[:300]}")

    if "error" in data:
        raise Exception(f"OpenRouter Error: {json.dumps(data['error'], indent=2)}")

    # === Extract AI response ===
    ai_text = data["choices"][0]["message"]["content"]

    # 🧹 Clean markdown wrapper or stray text
    if "```" in ai_text:
        ai_text = ai_text.split("```json")[-1].split("```")[0].strip()
    elif not ai_text.strip().startswith("{"):
        start = ai_text.find("{")
        end = ai_text.rfind("}") + 1
        ai_text = ai_text[start:end].strip()

    print("🧩 Cleaned AI text preview:", ai_text[:200])

    # === Define absolute save path ===
    base_dir = os.path.dirname(__file__)               # → backend/services/
    data_dir = os.path.abspath(os.path.join(base_dir, "../data"))
    os.makedirs(data_dir, exist_ok=True)               # ✅ auto-create if not exist

    save_path = os.path.join(data_dir, "schedule.json")

    # === Save result ===
    try:
        parsed = json.loads(ai_text)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2)
        print(f"💾 Saved schedule JSON → {save_path}")
        return parsed
    except json.JSONDecodeError:
        # fallback save raw text if parsing fails
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(ai_text)
        raise Exception("AI response not valid JSON; saved raw text instead.")
