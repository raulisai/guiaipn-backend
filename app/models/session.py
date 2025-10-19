"""
Esquema de sesiones
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Session:
    """Sesión de usuario"""
    session_id: str
    user_id: str
    current_question: Optional[str] = None
    current_step: int = 0
    pause_position: int = 0
    is_paused: bool = False
    is_streaming: bool = False
    conversation_context: dict = None
    created_at: datetime = None
    last_activity: datetime = None
    
    def __post_init__(self):
        if self.conversation_context is None:
            self.conversation_context = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.last_activity is None:
            self.last_activity = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "current_question": self.current_question,
            "current_step": self.current_step,
            "pause_position": self.pause_position,
            "is_paused": self.is_paused,
            "is_streaming": self.is_streaming,
            "conversation_context": self.conversation_context,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }
