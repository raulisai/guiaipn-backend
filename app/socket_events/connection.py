"""
Eventos de conexión/desconexión de Socket.IO
"""
from flask_socketio import emit, disconnect
from app import socketio
from app.auth.supabase import verify_token
from app.services.session_service import SessionService


@socketio.on("connect")
def handle_connect(auth):
    """
    Maneja la conexión de un cliente
    """
    try:
        # Verificar autenticación
        token = auth.get("token") if auth else None
        
        if not token:
            emit("error", {
                "code": "AUTH_REQUIRED",
                "message": "Token de autenticación requerido"
            })
            disconnect()
            return
        
        # Verificar token
        user = verify_token(token)
        
        # Crear sesión
        session_service = SessionService()
        session_id = session_service.create_session(user["id"])
        
        emit("connection_established", {
            "session_id": session_id,
            "user_info": {
                "email": user.get("email"),
                "id": user.get("id")
            }
        })
        
        print(f"✓ Usuario conectado: {user.get('email')}")
        
    except Exception as e:
        print(f"Error en conexión: {e}")
        emit("error", {
            "code": "CONNECTION_ERROR",
            "message": str(e)
        })
        disconnect()


@socketio.on("disconnect")
def handle_disconnect():
    """
    Maneja la desconexión de un cliente
    """
    print("✓ Usuario desconectado")
