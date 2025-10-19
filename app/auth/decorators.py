"""
Decoradores de autenticación
"""
from functools import wraps
from flask import request, jsonify
from flask_socketio import disconnect, emit
from app.auth.supabase import verify_token


def require_auth(f):
    """
    Decorador para proteger rutas HTTP que requieren autenticación
    
    Espera un header: Authorization: Bearer <token>
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return jsonify({"error": "No se proporcionó token de autenticación"}), 401
        
        try:
            token = auth_header.replace("Bearer ", "")
            user = verify_token(token)
            request.user = user
            return f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 401
    
    return decorated_function


def require_auth_socket(f):
    """
    Decorador para proteger handlers de Socket.IO que requieren autenticación
    
    Espera que el cliente envíe el token en el payload del evento:
    socket.emit('event_name', { token: 'jwt_token', ...other_data })
    
    El usuario verificado se inyecta en el payload como 'user'
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # El primer argumento es el data del evento
        data = args[0] if args else {}
        
        if not isinstance(data, dict):
            emit("error", {
                "code": "INVALID_PAYLOAD",
                "message": "El payload debe ser un objeto"
            })
            return
        
        token = data.get("token")
        
        if not token:
            emit("error", {
                "code": "AUTH_REQUIRED",
                "message": "Token de autenticación requerido"
            })
            disconnect()
            return
        
        try:
            user = verify_token(token)
            # Inyectar usuario en el payload
            data["user"] = user
            return f(*args, **kwargs)
            
        except Exception as e:
            emit("error", {
                "code": "AUTH_FAILED",
                "message": f"Autenticación fallida: {str(e)}"
            })
            disconnect()
    
    return decorated_function
