"""
Servicio de gestión de sesiones de Socket.IO con Redis
Maneja la lógica de negocio, validaciones y orquestación
"""
import uuid
from datetime import datetime
from typing import Optional
from app.repositories.session_repository import SessionRepository
from app.extensions import get_redis


class SessionExpiredError(Exception):
    """Excepción cuando una sesión no existe o expiró"""
    pass


class SessionService:
    """
    Gestiona sesiones activas de Socket.IO usando Redis
    
    Cada sesión almacena:
    - Estado de conversación actual
    - Pregunta en proceso
    - Posición de streaming (pause/resume)
    - Contexto de conversación
    - Metadata de conexión
    """
    
    DEFAULT_TTL = 1800  # 30 minutos
    
    def __init__(self, session_repo: Optional[SessionRepository] = None):
        """
        Inicializa el servicio con repositorio
        
        Args:
            session_repo: Repositorio de sesiones (opcional, se crea si no se provee)
        """
        if session_repo is None:
            redis_client = get_redis()
            session_repo = SessionRepository(redis_client)
        
        self.repo = session_repo
    
    def create_session(self, user_id: str, connection_id: str = None) -> str:
        """
        Crea una nueva sesión para un usuario conectado
        
        Args:
            user_id: UUID del usuario
            connection_id: ID del socket (opcional)
            
        Returns:
            str: session_id generado (UUID)
            
        Raises:
            Exception: Si hay error al crear la sesión
        """
        session_id = str(uuid.uuid4())
        
        session_data = {
            "user_id": user_id,
            "connection_id": connection_id,
            "current_question": None,
            "current_step": 0,
            "pause_position": 0,
            "is_paused": False,
            "is_streaming": False,
            "conversation_context": {},
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }
        
        self.repo.create(session_id, session_data, ttl=self.DEFAULT_TTL)
        
        print(f"✓ Sesión creada: {session_id} para usuario: {user_id}")
        
        return session_id
    
    def get_session(self, session_id: str) -> dict:
        """
        Obtiene una sesión y actualiza su actividad
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            dict: Datos de la sesión
            
        Raises:
            SessionExpiredError: Si la sesión no existe o expiró
        """
        session = self.repo.get(session_id)
        
        if session is None:
            raise SessionExpiredError(f"Sesión {session_id} no existe o expiró")
        
        # Actualizar last_activity y renovar TTL
        session["last_activity"] = datetime.utcnow().isoformat()
        self.repo.update(session_id, {"last_activity": session["last_activity"]})
        
        return session
    
    def update_session(self, session_id: str, data: dict) -> bool:
        """
        Actualiza campos específicos de una sesión
        
        Args:
            session_id: ID de la sesión
            data: Datos a actualizar (se hace merge)
            
        Returns:
            bool: True si se actualizó exitosamente
            
        Raises:
            SessionExpiredError: Si la sesión no existe
        """
        # Validar que la sesión existe
        if not self.repo.exists(session_id):
            raise SessionExpiredError(f"Sesión {session_id} no existe")
        
        # Agregar timestamp de última actividad
        data["last_activity"] = datetime.utcnow().isoformat()
        
        # Actualizar y renovar TTL
        self.repo.update(session_id, data, ttl=self.DEFAULT_TTL)
        
        return True
    
    def renew_ttl(self, session_id: str) -> bool:
        """
        Renueva el TTL de una sesión sin modificar datos
        Útil para keep-alive
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            bool: True si se renovó exitosamente
        """
        return self.repo.renew_ttl(session_id, ttl=self.DEFAULT_TTL)
    
    def end_session(self, session_id: str) -> bool:
        """
        Finaliza una sesión (disconnect limpio)
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            bool: True si se eliminó exitosamente
        """
        # Opcional: Aquí podrías guardar estadísticas en Supabase
        # antes de eliminar la sesión
        
        success = self.repo.delete(session_id)
        
        if success:
            print(f"✓ Sesión finalizada: {session_id}")
        
        return success
    
    def session_exists(self, session_id: str) -> bool:
        """
        Verifica si una sesión existe
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            bool: True si existe
        """
        return self.repo.exists(session_id)
    
    def get_session_ttl(self, session_id: str) -> int:
        """
        Obtiene el tiempo restante de una sesión
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            int: Segundos restantes, -1 si no tiene TTL, -2 si no existe
        """
        return self.repo.get_ttl(session_id)
    
    def cleanup_expired_sessions(self) -> int:
        """
        Limpieza manual de sesiones expiradas
        (Redis TTL hace esto automáticamente, esto es para debugging/monitoring)
        
        Returns:
            int: Número de sesiones activas encontradas
        """
        active_sessions = self.repo.get_all_sessions()
        print(f"ℹ Sesiones activas: {len(active_sessions)}")
        return len(active_sessions)
    
    def update_streaming_state(self, session_id: str, is_streaming: bool, 
                               current_step: int = 0) -> bool:
        """
        Actualiza el estado de streaming de una sesión
        
        Args:
            session_id: ID de la sesión
            is_streaming: Si está en streaming
            current_step: Paso actual del streaming
            
        Returns:
            bool: True si se actualizó
        """
        return self.update_session(session_id, {
            "is_streaming": is_streaming,
            "current_step": current_step
        })
    
    def pause_streaming(self, session_id: str, pause_position: int) -> bool:
        """
        Pausa el streaming en una posición específica
        
        Args:
            session_id: ID de la sesión
            pause_position: Posición donde se pausó (caracteres procesados)
            
        Returns:
            bool: True si se pausó
        """
        return self.update_session(session_id, {
            "is_paused": True,
            "pause_position": pause_position,
            "is_streaming": False
        })
    
    def resume_streaming(self, session_id: str) -> dict:
        """
        Reanuda el streaming desde donde se pausó
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            dict: Datos de la sesión con pause_position
            
        Raises:
            SessionExpiredError: Si la sesión no existe
        """
        # Actualizar estado
        self.update_session(session_id, {
            "is_paused": False,
            "is_streaming": True
        })
        
        # Obtener sesión actualizada
        session = self.get_session(session_id)
        
        return session
