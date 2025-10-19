"""
Rutas de autenticación
"""
from flask import Blueprint, request, jsonify
from app.auth import verify_token, require_auth
from app.auth.supabase import get_user_profile

bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@bp.route("/verify", methods=["POST"])
def verify():
    """
    Verifica un token de Supabase
    """
    try:
        data = request.get_json()
        token = data.get("token")
        
        if not token:
            return jsonify({"error": "Token requerido"}), 400
        
        user = verify_token(token)
        profile = get_user_profile(user["id"])
        
        return jsonify({
            "user": user,
            "profile": profile
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 401


@bp.route("/profile", methods=["GET"])
@require_auth
def get_profile():
    """
    Obtiene el perfil del usuario autenticado
    """
    try:
        user_id = request.user["id"]
        profile = get_user_profile(user_id)
        
        if not profile:
            return jsonify({"error": "Perfil no encontrado"}), 404
        
        return jsonify(profile), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
