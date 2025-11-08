# backend/auth.py
import os
from datetime import datetime, timedelta
from functools import wraps

from flask import Blueprint, current_app, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from dotenv import load_dotenv

load_dotenv()

# --------- Configuration / DB init helpers ---------
db = SQLAlchemy()
DEFAULT_DB_PATH = "backend/data/users.db"
os.makedirs(os.path.dirname(DEFAULT_DB_PATH), exist_ok=True)

def init_auth_db(app, db_path=None):
    """
    Initialize SQLAlchemy on the provided Flask app.
    Call this from your app.py before register_blueprint or after creating app.
    """
    if db_path is None:
        db_path = DEFAULT_DB_PATH

    app.config.setdefault("SQLALCHEMY_DATABASE_URI", f"sqlite:///{db_path}")
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    # Secret for signing tokens (fallback to environment)
    app.config.setdefault("SECRET_KEY", os.getenv("SECRET_KEY", "dev-secret-placeholder"))
    # JWT expiration in seconds
    app.config.setdefault("JWT_EXP_SECONDS", int(os.getenv("JWT_EXP_SECONDS", "3600")))

    db.init_app(app)
    # create tables if they don't exist
    with app.app_context():
        db.create_all()

# --------- Models ---------
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "username": self.username, "created_at": self.created_at.isoformat()}

# --------- Helpers: password & JWT ---------
def hash_password(password: str) -> str:
    return generate_password_hash(password)

def check_password(password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, password)

def create_token(payload: dict, expires_seconds: int, secret: str):
    exp = datetime.utcnow() + timedelta(seconds=expires_seconds)
    payload = payload.copy()
    payload.update({"exp": exp, "iat": datetime.utcnow()})
    token = jwt.encode(payload, secret, algorithm="HS256")
    # pyjwt returns bytes in some versions; make sure to return str
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token

def decode_token(token: str, secret: str):
    return jwt.decode(token, secret, algorithms=["HS256"])

# --------- Auth blueprint & routes ---------
auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")

def token_required(f):
    """Decorator that requires a valid JWT in Authorization header: 'Bearer <token>'"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"error": "Invalid Authorization header"}), 401
        token = parts[1]
        secret = current_app.config["SECRET_KEY"]
        try:
            data = decode_token(token, secret)
            # attach the token payload (e.g., user_id) to request context via kwargs
            request.user = data
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated

@auth_bp.route("/signup", methods=["POST"])
def signup():
    """
    Expected JSON body: { "username": "alice", "password": "secret" }
    Creates a new user; returns 201 on success.
    """
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    # Basic validation rules (extend as you wish)
    if len(password) < 6:
        return jsonify({"error": "password must be at least 6 characters"}), 400

    # Check if username exists
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "username already taken"}), 400

    # Create user
    new_user = User(username=username, password_hash=hash_password(password))
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "user created", "user": new_user.to_dict()}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Expected JSON body: { "username": "alice", "password": "secret" }
    Returns { token: "...", expires_in: seconds, user: {...} } on success.
    """
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "username and password required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password(password, user.password_hash):
        return jsonify({"error": "invalid credentials"}), 401

    secret = current_app.config["SECRET_KEY"]
    expires = current_app.config["JWT_EXP_SECONDS"]
    token_payload = {"user_id": user.id, "username": user.username}
    token = create_token(token_payload, expires, secret)

    return jsonify({
        "message": "login successful",
        "token": token,
        "expires_in": expires,
        "user": user.to_dict()
    }), 200

@auth_bp.route("/me", methods=["GET"])
@token_required
def me():
    """Protected route that returns the token payload / user info (example)."""
    payload = getattr(request, "user", {})
    user_id = payload.get("user_id")
    if user_id is None:
        return jsonify({"error": "invalid token payload"}), 401
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404
    return jsonify({"user": user.to_dict()}), 200

# Optional: route to refresh token (simple form)
@auth_bp.route("/refresh", methods=["POST"])
@token_required
def refresh():
    """Refresh token: issues a new token with a new expiry for the same user."""
    payload = getattr(request, "user", {})
    user_id = payload.get("user_id")
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404

    secret = current_app.config["SECRET_KEY"]
    expires = current_app.config["JWT_EXP_SECONDS"]
    token_payload = {"user_id": user.id, "username": user.username}
    new_token = create_token(token_payload, expires, secret)

    return jsonify({"token": new_token, "expires_in": expires}), 200
