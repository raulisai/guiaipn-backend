"""
Eventos de conexión/desconexión de Socket.IO
"""
from flask import request
from flask_socketio import emit, disconnect
from app import socketio
from app.auth.supabase import verify_token
from app.services.session_service import SessionService


# Diccionario temporal para mapear socket_id -> session_id
# En producción, considera usar Redis para esto
active_connections = {}


@socketio.on("connect")
def handle_connect(auth):
    """
    Maneja la conexión de un cliente WebSocket
    
    Flujo:
    1. Valida token JWT
    2. Crea sesión en Redis con TTL 30 min
    3. Mapea connection_id -> session_id
    4. Emite confirmación al cliente
    """
    try:
        # Verificar autenticación
        token = auth.get("token") if auth else None
        
        if not token:
            print("✗ Conexión rechazada: Token no proporcionado")
            return False  # Rechazar conexión sin emitir eventos
        
        # Verificar token
        user = verify_token(token)
        
        # Obtener connection_id del socket
        connection_id = request.sid
        
        # Crear sesión en Redis
        session_service = SessionService()
        session_id = session_service.create_session(
            user_id=user["id"],
            connection_id=connection_id
        )
        
        # Mapear connection -> session para disconnect
        active_connections[connection_id] = session_id
        
        emit("connection_established", {
            "session_id": session_id,
            "user_info": {
                "email": user.get("email"),
                "id": user.get("id")
            }
        })
        
        print(f"✓ Usuario conectado: {user.get('email')} | Session: {session_id}")
        
    except Exception as e:
        print(f"✗ Error en conexión: {e}")
        import traceback
        traceback.print_exc()
        return False  # Rechazar conexión en caso de error


@socketio.on("disconnect")
def handle_disconnect():
    """
    Maneja la desconexión de un cliente
    
    Limpia la sesión de Redis y el mapeo local
    """
    try:
        connection_id = request.sid
        session_id = active_connections.get(connection_id)
        
        if session_id:
            # Finalizar sesión en Redis
            session_service = SessionService()
            session_service.end_session(session_id)
            
            # Limpiar mapeo local
            del active_connections[connection_id]
            
            print(f"✓ Usuario desconectado | Session: {session_id}")
        else:
            print("✓ Usuario desconectado (sin sesión)")
            
    except Exception as e:
        print(f"✗ Error en desconexión: {e}")
