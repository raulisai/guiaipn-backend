"""
Rutas de sesiones de estudio
"""
from flask import Blueprint, request, jsonify
from app.auth import require_auth

bp = Blueprint("sessions", __name__, url_prefix="/api/v1/sessions")


@bp.route("/", methods=["GET"])
@require_auth
def list_sessions():
    """
    Lista las sesiones del usuario
    """
    try:
        # TODO: Implementar con repository
        return jsonify({
            "sessions": [],
            "total": 0
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/<session_id>", methods=["GET"])
@require_auth
def get_session(session_id):
    """
    Obtiene una sesión específica
    """
    try:
        # TODO: Implementar con repository
        return jsonify({"message": "Not implemented"}), 501
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
