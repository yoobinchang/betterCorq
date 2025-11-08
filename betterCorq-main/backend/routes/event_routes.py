# backend/routes/event_routes.py
from flask import Blueprint, jsonify, request
from services.event_service import get_all_events, recommend_events
from services.schedule_service import load_schedule

event_bp = Blueprint("event_bp", __name__)

@event_bp.route("/recommend-events", methods=["POST"])
def recommend_events_route():
    """
    Receives user-selected days and tolerance (in minutes),
    then matches events that fit within user's free time.
    """
    try:
        body = request.get_json()
        selected_days = body.get("selected_days", [])
        tolerance = int(body.get("tolerance", 10))  # default fallback = 10min

        schedule_data = load_schedule()
        events = get_all_events()

        recommended = recommend_events(events, schedule_data, selected_days, tolerance)

        return jsonify({
            "message": "✅ Recommended events generated successfully.",
            "selected_days": selected_days,
            "tolerance_minutes": tolerance,
            "recommendations": recommended
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
