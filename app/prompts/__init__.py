"""
Prompts modulares para IA
Organiza todos los prompts del sistema en un solo lugar
"""
from .exam_prompts import get_exam_question_prompt
from .clarification_prompts import get_clarification_prompt
from .follow_up_prompts import get_follow_up_prompt
from .question_prompts import get_free_question_prompt

__all__ = [
    'get_exam_question_prompt',
    'get_clarification_prompt',
    'get_follow_up_prompt',
    'get_free_question_prompt'
]
