# backend/routes/ai_routes.py
from flask import Blueprint, request, jsonify
from services.ai_service import extract_schedule_from_image

ai_bp = Blueprint("ai_bp", __name__)

@ai_bp.route("/upload-schedule", methods=["POST"])
def upload_schedule():
    """
    Handle schedule image upload and extract schedule data using AI (Gemini Vision)
    """
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        # AI service handles schedule extraction
        extracted_data = extract_schedule_from_image(file)

        return jsonify({
            "message": "✅ Schedule extracted successfully",
            "data": extracted_data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
