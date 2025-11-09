# backend/app.py
from flask import Flask
from flask_cors import CORS

# === Import Blueprints ===
from routes.ai_routes import ai_bp          # AI image upload + free-time preview
from routes.schedule_routes import schedule_bp  # Save free time & match events
from routes.event_routes import event_bp    # Fetch/recommend events

# === Create Flask App ===
app = Flask(__name__)
CORS(app)  # ✅ Allow frontend (e.g., localhost:3000 / 5173)

# === Register Blueprints with prefixes ===
app.register_blueprint(ai_bp, url_prefix="/api/ai")
app.register_blueprint(schedule_bp, url_prefix="/api/schedule")
app.register_blueprint(event_bp, url_prefix="/api/events")

# === Root route (Health Check) ===
@app.route("/")
def home():
    """Simple health check route to confirm backend is live."""
    return {
        "message": "✅ betterCorq backend is running",
        "available_routes": {
            "POST /api/ai/upload-schedule": "Upload schedule image → AI extract → free time preview",
            "POST /api/schedule/save-free-time": "Save final user-selected free time",
            "GET  /api/schedule/generate-matched-events": "Generate events that fit user free time",
            "GET  /api/events/recommend": "Fetch recommended events (auto-update)"
        }
    }

# === Run Flask ===
if __name__ == "__main__":
    app.run(debug=True, port=5000)
