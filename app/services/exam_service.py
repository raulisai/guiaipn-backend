"""
Servicio para gestionar explicaciones de preguntas de examen
"""
from typing import Optional
from app.repositories.question_repo import QuestionRepository
from app.repositories.exam_explanation_repo import ExamExplanationRepository
from app.models.explanation import ExamExplanation, ExplanationStep


class ExamService:
    """
    Gestiona el flujo de preguntas de examen y sus explicaciones
    
    Responsabilidades:
    - Obtener preguntas aleatorias por materia
    - Validar respuestas del usuario
    - Obtener o crear explicaciones
    - Actualizar estadísticas
    """
    
    def __init__(
        self,
        question_repo: Optional[QuestionRepository] = None,
        explanation_repo: Optional[ExamExplanationRepository] = None
    ):
        """
        Inicializa el servicio
        
        Args:
            question_repo: Repositorio de preguntas
            explanation_repo: Repositorio de explicaciones
        """
        self.question_repo = question_repo or QuestionRepository()
        self.explanation_repo = explanation_repo or ExamExplanationRepository()
    
    def get_random_question(self, subject: str, difficulty: str = None) -> Optional[dict]:
        """
        Obtiene una pregunta aleatoria por materia
        
        Args:
            subject: Materia (matematicas, fisica, etc)
            difficulty: Dificultad opcional (easy, medium, hard)
            
        Returns:
            dict: Pregunta o None
        """
        return self.question_repo.get_random_by_subject(subject, difficulty)
    
    def validate_answer(self, question_id: str, user_answer: str) -> dict:
        """
        Valida la respuesta del usuario
        
        Args:
            question_id: UUID de la pregunta
            user_answer: Respuesta del usuario (a, b, c, d)
            
        Returns:
            dict: {
                "correct": bool,
                "correct_answer": str,
                "message": str
            }
        """
        question = self.question_repo.get_by_id(question_id)
        
        if not question:
            return {
                "correct": False,
                "correct_answer": None,
                "message": "Pregunta no encontrada"
            }
        
        is_correct = user_answer.lower() == question["correct_answer"].lower()
        
        # Actualizar estadísticas
        self.question_repo.increment_stats(question_id, is_correct)
        
        if is_correct:
            return {
                "correct": True,
                "correct_answer": question["correct_answer"],
                "message": "¡Correcto!"
            }
        else:
            return {
                "correct": False,
                "correct_answer": question["correct_answer"],
                "message": f"Incorrecto. La respuesta correcta es {question['correct_answer']}"
            }
    
    def get_or_create_explanation(
        self,
        question_id: str,
        ai_model: str = "gpt-4",
        prompt_version: str = "v1.0"
    ) -> Optional[dict]:
        """
        Obtiene explicación existente o retorna None para generar nueva
        
        Args:
            question_id: UUID de la pregunta
            ai_model: Modelo de IA usado
            prompt_version: Versión del prompt
            
        Returns:
            dict: Explicación si existe, None si debe generarse
        """
        # Buscar explicación existente
        explanation = self.explanation_repo.get_by_question_id(question_id)
        
        if explanation:
            # Incrementar contador de uso
            self.explanation_repo.increment_usage(explanation["id"])
            return explanation
        
        # No existe - debe generarse con IA
        return None
    
    def create_explanation(
        self,
        question_id: str,
        explanation_steps: list,
        total_duration: int,
        ai_model: str = "gpt-4",
        prompt_version: str = "v1.0"
    ) -> Optional[dict]:
        """
        Crea una nueva explicación
        
        Args:
            question_id: UUID de la pregunta
            explanation_steps: Lista de pasos de la explicación
            total_duration: Duración estimada en segundos
            ai_model: Modelo de IA usado
            prompt_version: Versión del prompt
            
        Returns:
            dict: Explicación creada
        """
        data = {
            "question_id": question_id,
            "explanation_steps": explanation_steps,
            "total_duration": total_duration,
            "ai_model": ai_model,
            "prompt_version": prompt_version,
            "generated_by": "ai",
            "usage_count": 1
        }
        
        return self.explanation_repo.create(data)
    
    def record_feedback(
        self,
        explanation_id: str,
        is_helpful: bool,
        flag_reason: Optional[str] = None
    ):
        """
        Registra feedback del usuario sobre una explicación
        
        Args:
            explanation_id: UUID de la explicación
            is_helpful: Si fue marcada como útil
            flag_reason: Razón del flag si existe
        """
        self.explanation_repo.record_feedback(
            explanation_id,
            is_helpful,
            flag_reason
        )
    
    def get_question_with_explanation(self, question_id: str) -> Optional[dict]:
        """
        Obtiene pregunta con su explicación (si existe)
        
        Args:
            question_id: UUID de la pregunta
            
        Returns:
            dict: {
                "question": dict,
                "explanation": dict | None
            }
        """
        question = self.question_repo.get_by_id(question_id)
        
        if not question:
            return None
        
        explanation = self.explanation_repo.get_by_question_id(question_id)
        
        return {
            "question": question,
            "explanation": explanation
        }
