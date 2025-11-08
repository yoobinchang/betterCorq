# backend/routes/event_routes.py
from flask import Blueprint, jsonify
from services.event_service import load_events, recommend_events

event_bp = Blueprint("event_bp", __name__)

@event_bp.route("/get-events", methods=["GET"])
def get_events():
    """Return all events from events_est.json"""
    try:
        events = load_events()
        return jsonify(events), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@event_bp.route("/recommend-events", methods=["GET"])
def get_recommendations():
    """Recommend events based on user's free time"""
    try:
        recommended = recommend_events()
        return jsonify({
            "message": "✅ Recommended events generated",
            "count": len(recommended),
            "events": recommended
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
