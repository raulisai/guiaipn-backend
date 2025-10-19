"""
Repositorio de sesiones (Redis)
"""
import json
from app.extensions import get_redis
from app.config import Config


class SessionRepository:
    """Acceso a datos de sesiones en Redis"""
    
    def __init__(self):
        self.redis = get_redis()
        self.ttl = Config.SESSION_TTL
    
    def save(self, session_id: str, data: dict, ttl: int = None):
        """
        Guarda una sesión en Redis
        
        Args:
            session_id: ID de la sesión
            data: Datos a guardar
            ttl: Time to live en segundos (opcional)
        """
        key = f"session:{session_id}"
        ttl = ttl or self.ttl
        
        self.redis.setex(key, ttl, json.dumps(data))
    
    def get(self, session_id: str) -> dict:
        """
        Obtiene una sesión de Redis
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            dict: Datos de la sesión o None
        """
        key = f"session:{session_id}"
        data = self.redis.get(key)
        
        return json.loads(data) if data else None
    
    def delete(self, session_id: str):
        """
        Elimina una sesión
        
        Args:
            session_id: ID de la sesión
        """
        key = f"session:{session_id}"
        self.redis.delete(key)
    
    def exists(self, session_id: str) -> bool:
        """
        Verifica si existe una sesión
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            bool: True si existe
        """
        key = f"session:{session_id}"
        return self.redis.exists(key) > 0
