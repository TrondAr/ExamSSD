from flask import Blueprint, jsonify, request, abort
from services.auth_service import verify_password
from database import get_user_by_email
from utils.tokens import mint_api_token
from utils.decorators import requires_token

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.post("/login")
def api_login():
    data = request.get_json(force=True, silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    pwd   = data.get("password") or ""
    if not verify_password(email, pwd): return abort(401)
    user = get_user_by_email(email)
    token = mint_api_token(user["id"])
    return jsonify({"token": token, "role": user["role"]})

@api_bp.get("/me")
@requires_token("patient","practitioner","admin")
def me():
    return jsonify({"ok": True})