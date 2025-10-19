"""
Rutas de autenticación
"""
from flask import Blueprint, request, jsonify
from app.auth import verify_token, require_auth
from app.auth.supabase import get_user_profile, create_user_profile, initialize_user_progress

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
        
        return jsonify({
            "user": user,
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


@bp.route("/initialize", methods=["POST"])
def initialize_profile():
    """
    Inicializa el perfil de un nuevo usuario después del registro con Google OAuth.
    Crea el perfil en la tabla profiles y el progreso inicial en user_progress.
    """
    try:
        data = request.get_json()
        token = data.get("token")
        
        if not token:
            return jsonify({"error": "Token requerido"}), 400
        
        # Verificar token y obtener información del usuario
        user = verify_token(token)
        user_id = user["id"]
        email = user["email"]
        
        # Verificar si el perfil ya existe
        existing_profile = get_user_profile(user_id)
        if existing_profile:
            return jsonify({
                "message": "El perfil ya existe",
                "profile": existing_profile
            }), 200
        
        # Extraer información adicional del metadata de Google
        user_metadata = user.get("user_metadata", {})
        full_name = user_metadata.get("full_name") or user_metadata.get("name")
        avatar_url = user_metadata.get("avatar_url") or user_metadata.get("picture")
        
        # Crear perfil con valores por defecto
        profile = create_user_profile(
            user_id=user_id,
            email=email,
            full_name=full_name,
            avatar_url=avatar_url
        )
        
        # Inicializar progreso para todas las materias
        progress = initialize_user_progress(user_id)
        
        return jsonify({
            "message": "Perfil inicializado exitosamente",
            "profile": profile,
            "progress_initialized": len(progress)
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
