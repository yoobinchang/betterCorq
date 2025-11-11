from flask import Blueprint, jsonify
from services.schedule_service import generate_matched_events

event_bp = Blueprint("event_bp", __name__)

@event_bp.route("/api/events/recommend", methods=["GET"])
def get_recommended_events():
    """
    Returns events that fit within the user's saved free time.
    Automatically updates CORQ events before filtering.
    """
    try:
        result = generate_matched_events()
        return jsonify({
            "message": "Recommended events generated successfully.",
            "count": result["matched_events_count"],
            "events": result["matched_events"]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
