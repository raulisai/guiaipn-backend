"""
Servicio de gestión de sesiones (Redis)
"""
import uuid
import json
from datetime import datetime
from app.extensions import get_redis
from app.config import Config


class SessionService:
    """Gestiona sesiones de usuario en Redis"""
    
    def __init__(self):
        self.redis = get_redis()
        self.ttl = Config.SESSION_TTL
    
    def create_session(self, user_id: str) -> str:
        """
        Crea una nueva sesión para un usuario
        
        Args:
            user_id: UUID del usuario
            
        Returns:
            str: session_id generado
        """
        session_id = str(uuid.uuid4())
        
        session_data = {
            "user_id": user_id,
            "current_question": None,
            "current_step": 0,
            "pause_position": 0,
            "is_paused": False,
            "is_streaming": False,
            "conversation_context": {},
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }
        
        key = f"session:{session_id}"
        self.redis.setex(key, self.ttl, json.dumps(session_data))
        
        return session_id
    
    def get_session(self, session_id: str) -> dict:
        """
        Obtiene los datos de una sesión
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            dict: Datos de la sesión o None
        """
        key = f"session:{session_id}"
        data = self.redis.get(key)
        
        if data:
            session = json.loads(data)
            # Actualizar last_activity
            session["last_activity"] = datetime.utcnow().isoformat()
            self.redis.setex(key, self.ttl, json.dumps(session))
            return session
        
        return None
    
    def update_session(self, session_id: str, data: dict):
        """
        Actualiza datos de una sesión
        
        Args:
            session_id: ID de la sesión
            data: Datos a actualizar
        """
        session = self.get_session(session_id)
        
        if session:
            session.update(data)
            session["last_activity"] = datetime.utcnow().isoformat()
            
            key = f"session:{session_id}"
            self.redis.setex(key, self.ttl, json.dumps(session))
    
    def delete_session(self, session_id: str):
        """
        Elimina una sesión
        
        Args:
            session_id: ID de la sesión
        """
        key = f"session:{session_id}"
        self.redis.delete(key)
