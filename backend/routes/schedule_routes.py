# backend/routes/schedule_routes.py
from flask import Blueprint, jsonify, request
from services.schedule_service import load_schedule, save_schedule

schedule_bp = Blueprint("schedule_bp", __name__)

@schedule_bp.route("/get-schedule", methods=["GET"])
def get_schedule():
    """Return currently saved schedule.json"""
    try:
        schedule = load_schedule()
        return jsonify(schedule), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@schedule_bp.route("/update-schedule", methods=["POST"])
def update_schedule():
    """Allow manual update of schedule.json"""
    try:
        data = request.get_json()
        save_schedule(data)
        return jsonify({"message": "✅ Schedule updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500