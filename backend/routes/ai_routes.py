# backend/routes/ai_routes.py
from flask import Blueprint, request, jsonify
from services.ai_service import extract_schedule_from_image
from services.schedule_service import calc_free_time_only

ai_bp = Blueprint("ai_bp", __name__)

# === 1️⃣ Upload Schedule Image → AI Extract → Free Time Preview ===
@ai_bp.route("/upload-schedule", methods=["POST"])
def upload_schedule():
    """
    Handle schedule image upload:
    1️⃣ Send image to AI for busy-time extraction
    2️⃣ Convert busy → free time for frontend preview
    """
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        print(f"📸 File received: {file.filename}")

        # Step 1: AI extracts busy schedule (Mon, Tue, ...)
        busy = extract_schedule_from_image(file)

        # Step 2: Convert busy → free time (not saved yet)
        free_time = calc_free_time_only(busy)
        print("✅ Free time calculated successfully")

        # Step 3: Return free-time preview to frontend
        return jsonify({
            "message": "✅ Schedule extracted successfully",
            "data": free_time
        }), 200

    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return jsonify({"error": str(e)}), 500


# === 2️⃣ (Optional) Internal route — AI extract only ===
@ai_bp.route("/ai/extract-schedule", methods=["POST"])
def extract_schedule_only():
    """
    Internal test route:
    Extract busy schedule from uploaded image (without free-time conversion).
    """
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        result = extract_schedule_from_image(file)

        return jsonify({
            "message": "✅ Busy schedule extracted successfully",
            "data": result
        }), 200

    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return jsonify({"error": str(e)}), 500
