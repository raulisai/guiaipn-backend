"""
Servicio de procesamiento de preguntas
"""
from app.utils.text_processing import normalize_text, generate_hash
from app.repositories.ai_answers_repo import AIAnswersRepository
from app.services.ai_service import AIService


class QuestionService:
    """Procesa preguntas del usuario"""
    
    def __init__(self):
        self.ai_answers_repo = AIAnswersRepository()
        self.ai_service = AIService()
    
    def process_question(self, question: str, context: dict = None) -> dict:
        """
        Procesa una pregunta del usuario
        
        Args:
            question: Texto de la pregunta
            context: Contexto adicional (opcional)
            
        Returns:
            dict: Respuesta estructurada con pasos
        """
        # Normalizar y generar hash
        normalized = normalize_text(question)
        question_hash = generate_hash(normalized)
        
        # Buscar en cache/DB
        cached_answer = self.ai_answers_repo.get_by_hash(question_hash)
        
        if cached_answer:
            # Incrementar contador de uso
            self.ai_answers_repo.increment_usage(cached_answer["id"])
            
            return {
                "question_hash": question_hash,
                "question_text": question,
                "answer_steps": cached_answer["answer_steps"],
                "total_duration": cached_answer["total_duration"],
                "from_cache": True
            }
        
        # Generar con IA
        ai_response = self.ai_service.generate_answer(question, context)
        
        # Guardar en DB
        saved_answer = self.ai_answers_repo.create({
            "question_hash": question_hash,
            "question_text": question,
            "answer_steps": ai_response["steps"],
            "total_duration": ai_response["total_duration"],
            "generated_by": "gpt-4"
        })
        
        return {
            "question_hash": question_hash,
            "question_text": question,
            "answer_steps": ai_response["steps"],
            "total_duration": ai_response["total_duration"],
            "from_cache": False
        }
