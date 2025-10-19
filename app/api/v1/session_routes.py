"""
Rutas de sesiones de estudio
"""
from flask import Blueprint, request, jsonify
from app.auth import require_auth

bp = Blueprint("sessions", __name__, url_prefix="/api/v1/sessions")


@bp.route("/", methods=["GET"])
@require_auth
def list_sessions(current_user):
    """
    Lista las sesiones del usuario (activas en Redis)
    
    Nota: Las sesiones en Redis son temporales (TTL 30 min).
    Para historial persistente, consultar tabla 'interactions' en Supabase.
    """
    try:
        from app.services.session_service import SessionService
        
        # Las sesiones Redis son efímeras, solo retornamos info básica
        # En producción, esto podría consultar Supabase para historial
        return jsonify({
            "message": "Las sesiones activas se gestionan vía Socket.IO",
            "info": "Conéctate vía WebSocket para crear una sesión activa",
            "user_id": current_user["id"]
        }), 200
        
    except Exception as e:
        print(f"Error listando sesiones: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@bp.route("/<session_id>", methods=["GET"])
@require_auth
def get_session(current_user, session_id):
    """
    Obtiene una sesión específica de Redis
    """
    try:
        from app.services.session_service import SessionService, SessionExpiredError
        
        session_service = SessionService()
        
        try:
            session = session_service.get_session(session_id)
            
            # Verificar que la sesión pertenece al usuario
            if session.get("user_id") != current_user["id"]:
                return jsonify({"error": "No autorizado"}), 403
            
            return jsonify(session), 200
            
        except SessionExpiredError:
            return jsonify({"error": "Sesión expirada o no encontrada"}), 404
        
    except Exception as e:
        print(f"Error obteniendo sesión: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500
