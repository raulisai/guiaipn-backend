"""
Servicio para generar y gestionar explicaciones
Wrapper sobre AIService para diferentes tipos de explicaciones
"""
from typing import Optional, Dict
from app.services.ai_service import AIService


class ExplanationService:
    """
    Servicio de alto nivel para generar explicaciones
    
    Responsabilidades:
    - Coordinar generación de explicaciones con IA
    - Aplicar lógica de negocio específica
    - Formatear respuestas según el tipo
    """
    
    def __init__(self, ai_service: Optional[AIService] = None):
        """
        Inicializa el servicio
        
        Args:
            ai_service: Servicio de IA (opcional)
        """
        self.ai_service = ai_service or AIService()
    
    def generate_exam_explanation(
        self,
        question: dict,
        user_answer: str = None
    ) -> Dict:
        """
        Genera explicación para pregunta de examen
        
        Args:
            question: Datos de la pregunta
            user_answer: Respuesta del usuario (opcional)
            
        Returns:
            dict: Explicación estructurada
        """
        return self.ai_service.generate_exam_explanation(question, user_answer)
    
    def generate_clarification(
        self,
        clarification_question: str,
        current_context: dict
    ) -> Dict:
        """
        Genera aclaración rápida
        
        Args:
            clarification_question: Pregunta del usuario
            current_context: Contexto actual
            
        Returns:
            dict: Aclaración estructurada
        """
        return self.ai_service.generate_clarification(
            clarification_question,
            current_context
        )
    
    def generate_follow_up(
        self,
        follow_up_question: str,
        original_question: dict,
        previous_explanation: dict = None
    ) -> Dict:
        """
        Genera respuesta a pregunta adicional
        
        Args:
            follow_up_question: Pregunta adicional
            original_question: Pregunta original
            previous_explanation: Explicación previa (opcional)
            
        Returns:
            dict: Respuesta estructurada
        """
        return self.ai_service.generate_follow_up(
            follow_up_question,
            original_question,
            previous_explanation
        )
    
    def generate_free_question_answer(
        self,
        question: str,
        context: dict = None
    ) -> Dict:
        """
        Genera respuesta para pregunta libre
        
        Args:
            question: Pregunta del usuario
            context: Contexto adicional (opcional)
            
        Returns:
            dict: Respuesta estructurada
        """
        # Usar el método existente de AIService
        return self.ai_service.generate_answer(question, context)
    
    def validate_explanation_quality(self, explanation: dict) -> float:
        """
        Valida la calidad de una explicación
        
        Args:
            explanation: Explicación a validar
            
        Returns:
            float: Score de calidad (0.0 a 1.0)
        """
        score = 0.0
        
        # Verificar que tenga pasos
        steps = explanation.get('explanation_steps', []) or explanation.get('answer_steps', [])
        if not steps:
            return 0.0
        
        # Puntos por número de pasos (ideal: 3-5)
        num_steps = len(steps)
        if 3 <= num_steps <= 5:
            score += 0.3
        elif num_steps > 0:
            score += 0.1
        
        # Puntos por contenido en cada paso
        for step in steps:
            if step.get('title') and len(step.get('title', '')) > 5:
                score += 0.1
            if step.get('content') and len(step.get('content', '')) > 20:
                score += 0.1
        
        # Normalizar score
        score = min(score, 1.0)
        
        return round(score, 2)
