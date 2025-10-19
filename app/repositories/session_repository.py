"""
Repositorio para operaciones CRUD de sesiones en Redis
"""
import json
from typing import Optional
from redis import Redis


class SessionRepository:
    """
    Maneja operaciones directas con Redis para sesiones
    Formato: session:{session_id}
    """
    
    def __init__(self, redis_client: Redis):
        """
        Inicializa el repositorio con cliente Redis
        
        Args:
            redis_client: Cliente Redis configurado
        """
        self.redis = redis_client
        self.key_prefix = "session:"
    
    def _get_key(self, session_id: str) -> str:
        """Genera la key completa para Redis"""
        return f"{self.key_prefix}{session_id}"
    
    def create(self, session_id: str, data: dict, ttl: int = 1800) -> bool:
        """
        Crea una nueva sesión en Redis con TTL
        
        Args:
            session_id: ID único de la sesión
            data: Datos de la sesión
            ttl: Tiempo de vida en segundos (default: 1800 = 30 min)
            
        Returns:
            bool: True si se creó exitosamente
            
        Raises:
            Exception: Si hay error al guardar en Redis
        """
        try:
            key = self._get_key(session_id)
            json_data = json.dumps(data, default=str)
            return self.redis.setex(key, ttl, json_data)
        except Exception as e:
            raise Exception(f"Error creando sesión en Redis: {str(e)}")
    
    def get(self, session_id: str) -> Optional[dict]:
        """
        Obtiene una sesión de Redis
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            dict | None: Datos de la sesión o None si no existe/expiró
        """
        try:
            key = self._get_key(session_id)
            data = self.redis.get(key)
            
            if data is None:
                return None
            
            return json.loads(data)
        except json.JSONDecodeError as e:
            print(f"Error decodificando sesión {session_id}: {e}")
            return None
        except Exception as e:
            print(f"Error obteniendo sesión {session_id}: {e}")
            return None
    
    def update(self, session_id: str, data: dict, ttl: int = 1800) -> bool:
        """
        Actualiza una sesión existente (merge con datos actuales)
        
        Args:
            session_id: ID de la sesión
            data: Datos a actualizar (se hace merge)
            ttl: Nuevo TTL en segundos
            
        Returns:
            bool: True si se actualizó exitosamente
            
        Raises:
            Exception: Si la sesión no existe o hay error
        """
        try:
            # Obtener sesión actual
            current_data = self.get(session_id)
            
            if current_data is None:
                raise Exception(f"Sesión {session_id} no existe")
            
            # Merge datos
            current_data.update(data)
            
            # Guardar con TTL renovado
            key = self._get_key(session_id)
            json_data = json.dumps(current_data, default=str)
            return self.redis.setex(key, ttl, json_data)
            
        except Exception as e:
            raise Exception(f"Error actualizando sesión: {str(e)}")
    
    def delete(self, session_id: str) -> bool:
        """
        Elimina una sesión de Redis
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            bool: True si se eliminó (o no existía)
        """
        try:
            key = self._get_key(session_id)
            self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Error eliminando sesión {session_id}: {e}")
            return False
    
    def renew_ttl(self, session_id: str, ttl: int = 1800) -> bool:
        """
        Renueva el TTL de una sesión sin modificar datos
        
        Args:
            session_id: ID de la sesión
            ttl: Nuevo TTL en segundos
            
        Returns:
            bool: True si se renovó exitosamente
        """
        try:
            key = self._get_key(session_id)
            return self.redis.expire(key, ttl)
        except Exception as e:
            print(f"Error renovando TTL de sesión {session_id}: {e}")
            return False
    
    def exists(self, session_id: str) -> bool:
        """
        Verifica si una sesión existe en Redis
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            bool: True si existe
        """
        try:
            key = self._get_key(session_id)
            return self.redis.exists(key) > 0
        except Exception as e:
            print(f"Error verificando existencia de sesión {session_id}: {e}")
            return False
    
    def get_ttl(self, session_id: str) -> int:
        """
        Obtiene el TTL restante de una sesión
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            int: Segundos restantes, -1 si no tiene TTL, -2 si no existe
        """
        try:
            key = self._get_key(session_id)
            return self.redis.ttl(key)
        except Exception as e:
            print(f"Error obteniendo TTL de sesión {session_id}: {e}")
            return -2
    
    def get_all_sessions(self) -> list[str]:
        """
        Obtiene todos los IDs de sesiones activas (para debugging)
        
        Returns:
            list[str]: Lista de session_ids
        """
        try:
            pattern = f"{self.key_prefix}*"
            keys = self.redis.keys(pattern)
            # Remover el prefijo de cada key
            return [key.replace(self.key_prefix, "") for key in keys]
        except Exception as e:
            print(f"Error obteniendo todas las sesiones: {e}")
            return []
