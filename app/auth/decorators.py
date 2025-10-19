"""
Decoradores de autenticación
"""
from functools import wraps
from flask import request, jsonify
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
