"""
Modelo para explicaciones de preguntas de examen
"""
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ExplanationStep:
    """Paso individual de una explicación"""
    step_number: int
    title: str
    content: str
    content_type: str = "text"
    has_visual: bool = False
    canvas_commands: Optional[List[dict]] = None


@dataclass
class ExamExplanation:
    """Explicación completa de pregunta de examen"""
    id: Optional[str]
    question_id: str
    steps: List[ExplanationStep]
    total_duration: int
    quality_score: float = 0.00
    is_verified: bool = False
    is_flagged: bool = False
    flag_reason: Optional[str] = None
    usage_count: int = 0
    helpful_votes: int = 0
    unhelpful_votes: int = 0
    total_votes: int = 0
    generated_by: str = "ai"
    ai_model: Optional[str] = None
    prompt_version: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convierte a diccionario para guardar en DB"""
        return {
            "question_id": self.question_id,
            "explanation_steps": [
                {
                    "step_number": step.step_number,
                    "title": step.title,
                    "content": step.content,
                    "content_type": step.content_type,
                    "has_visual": step.has_visual,
                    "canvas_commands": step.canvas_commands
                }
                for step in self.steps
            ],
            "total_duration": self.total_duration,
            "quality_score": self.quality_score,
            "is_verified": self.is_verified,
            "is_flagged": self.is_flagged,
            "flag_reason": self.flag_reason,
            "usage_count": self.usage_count,
            "helpful_votes": self.helpful_votes,
            "unhelpful_votes": self.unhelpful_votes,
            "total_votes": self.total_votes,
            "generated_by": self.generated_by,
            "ai_model": self.ai_model,
            "prompt_version": self.prompt_version
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ExamExplanation':
        """Crea instancia desde diccionario de DB"""
        steps = [
            ExplanationStep(**step_data)
            for step_data in data.get("explanation_steps", [])
        ]
        
        return cls(
            id=data.get("id"),
            question_id=data["question_id"],
            steps=steps,
            total_duration=data.get("total_duration", 60),
            quality_score=float(data.get("quality_score", 0.00)),
            is_verified=data.get("is_verified", False),
            is_flagged=data.get("is_flagged", False),
            flag_reason=data.get("flag_reason"),
            usage_count=data.get("usage_count", 0),
            helpful_votes=data.get("helpful_votes", 0),
            unhelpful_votes=data.get("unhelpful_votes", 0),
            total_votes=data.get("total_votes", 0),
            generated_by=data.get("generated_by", "ai"),
            ai_model=data.get("ai_model"),
            prompt_version=data.get("prompt_version"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
