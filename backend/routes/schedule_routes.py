# backend/routes/schedule_routes.py

from flask import Blueprint, jsonify, request
from services.schedule_service import (
    save_user_free_time,
    generate_free_time as generate_matched_events  # ✅ alias로 이름 통일
)


schedule_bp = Blueprint("schedule_bp", __name__)

# === 1️⃣ Save User's Final Free Time Selection ===
@schedule_bp.route("/save-free-time", methods=["POST"])
def save_free_time():
    """
    Save the free time schedule selected and adjusted by the user.
    This replaces the old 'update-schedule' logic.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No free time data received"}), 400

        result = save_user_free_time(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# === 2️⃣ Match Events Based on Saved Free Time ===
@schedule_bp.route("/generate-matched-events", methods=["GET"])
def generate_matched_events_route():
    """
    1. Load the saved free_time.json
    2. Fetch the latest events from CORQ
    3. Match them against the user's free time
    4. Save and return matched events
    """
    try:
        result = generate_matched_events()
        return jsonify({
            "message": "✅ Events matched successfully.",
            "matched_events_count": result["matched_events_count"],
            "matched_events": result["matched_events"]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
