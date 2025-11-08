# backend/app.py
from flask import Flask
from routes.ai_routes import ai_bp
from routes.event_routes import event_bp
from routes.schedule_routes import schedule_bp

# create Flask app
app = Flask(__name__)

# Register Blueprints
# Each route file is defined separately and imported here
app.register_blueprint(ai_bp)
app.register_blueprint(event_bp)
app.register_blueprint(schedule_bp)

# Health check route
@app.route("/")
def home():
    return {
        "message": "✅ betterCorq backend is running",
        "available_routes": {
            "/upload-schedule": "POST - Upload schedule image for AI analysis",
            "/get-schedule": "GET - Get the current saved schedule",
            "/get-events": "GET - Return all campus events",
            "/recommend-events": "GET - Recommend events based on free time"
        }
    }

# Run Flask
if __name__ == "__main__":
    # debug=True enables auto-reload when code changes
    app.run(debug=True, port=5000)
