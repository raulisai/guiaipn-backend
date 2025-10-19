"""
Esquema de interacciones de voz
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class VoiceInteraction:
    """Interacción de voz"""
    session_id: str
    audio_data: bytes
    duration_ms: int
    transcription: Optional[str] = None
    confidence: Optional[float] = None
    language: str = "es"
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        return {
            "session_id": self.session_id,
            "duration_ms": self.duration_ms,
            "transcription": self.transcription,
            "confidence": self.confidence,
            "language": self.language
        }
