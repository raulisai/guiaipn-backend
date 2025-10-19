"""
Esquema de respuestas IA
"""
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class AnswerStep:
    """Paso individual de una respuesta"""
    step_number: int
    title: str
    content: str
    content_type: str = "text"
    has_visual: bool = False
    canvas_commands: Optional[List[dict]] = None


@dataclass
class Answer:
    """Respuesta completa estructurada (para preguntas libres y follow-ups)"""
    question_hash: str
    question_text: str
    steps: List[AnswerStep]
    total_duration: int
    generated_by: str = "manual"
    related_question_id: Optional[str] = None  # Para follow-up questions
    
    def to_dict(self) -> dict:
        """Convierte a diccionario"""
        data = {
            "question_hash": self.question_hash,
            "question_text": self.question_text,
            "answer_steps": [
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
            "generated_by": self.generated_by
        }
        
        if self.related_question_id:
            data["related_question_id"] = self.related_question_id
            
        return data
