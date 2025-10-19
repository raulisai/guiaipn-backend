"""
Servicio de procesamiento de preguntas
Valida, normaliza, genera hash y busca en cache
"""
from typing import Optional
from app.utils.text_processing import normalize_text, generate_hash
from app.repositories.ai_answers_repo import AIAnswersRepository


class QuestionValidationError(Exception):
    """Excepción cuando una pregunta no es válida"""
    pass


class QuestionService:
    """
    Procesa preguntas del usuario
    
    Responsabilidades:
    - Validar formato de pregunta
    - Normalizar texto
    - Generar hash SHA256
    - Buscar en cache (ai_answers)
    - Retornar answer_id si existe, None si no
    """
    
    MIN_QUESTION_LENGTH = 5
    MAX_QUESTION_LENGTH = 1000
    
    def __init__(self, ai_answers_repo: Optional[AIAnswersRepository] = None):
        """
        Inicializa el servicio
        
        Args:
            ai_answers_repo: Repositorio de respuestas (opcional)
        """
        if ai_answers_repo is None:
            ai_answers_repo = AIAnswersRepository()
        
        self.ai_answers_repo = ai_answers_repo
    
    def validate_question(self, question_text: str) -> None:
        """
        Valida que una pregunta cumpla con los requisitos
        
        Args:
            question_text: Texto de la pregunta
            
        Raises:
            QuestionValidationError: Si la pregunta no es válida
        """
        if not question_text or not isinstance(question_text, str):
            raise QuestionValidationError("La pregunta debe ser un texto no vacío")
        
        question_text = question_text.strip()
        
        if len(question_text) < self.MIN_QUESTION_LENGTH:
            raise QuestionValidationError(
                f"La pregunta debe tener al menos {self.MIN_QUESTION_LENGTH} caracteres"
            )
        
        if len(question_text) > self.MAX_QUESTION_LENGTH:
            raise QuestionValidationError(
                f"La pregunta no puede exceder {self.MAX_QUESTION_LENGTH} caracteres"
            )
    
    def process_question(self, user_id: str, question_text: str) -> dict:
        """
        Procesa una pregunta del usuario
        
        Flujo:
        1. Valida formato
        2. Normaliza texto
        3. Genera hash SHA256
        4. Busca en Supabase (ai_answers)
        5. Retorna answer_id si existe, None si no
        
        Args:
            user_id: UUID del usuario
            question_text: Texto de la pregunta
            
        Returns:
            dict: {
                "question_hash": str,
                "question_text": str,
                "normalized_text": str,
                "answer_id": UUID | None,
                "cached": bool
            }
            
        Raises:
            QuestionValidationError: Si la pregunta no es válida
        """
        # 1. Validar
        self.validate_question(question_text)
        
        # 2. Normalizar
        normalized = normalize_text(question_text)
        
        # 3. Generar hash
        question_hash = generate_hash(normalized)
        
        # 4. Buscar en cache/DB
        cached_answer = self.ai_answers_repo.get_by_hash(question_hash)
        
        if cached_answer:
            # Incrementar contador de uso
            self.ai_answers_repo.increment_usage(cached_answer["id"])
            
            return {
                "question_hash": question_hash,
                "question_text": question_text,
                "normalized_text": normalized,
                "answer_id": cached_answer["id"],
                "cached": True,
                "answer_steps": cached_answer.get("answer_steps"),
                "total_duration": cached_answer.get("total_duration")
            }
        
        # 5. No existe en cache - retornar None
        # La generación con IA se manejará en otro servicio
        return {
            "question_hash": question_hash,
            "question_text": question_text,
            "normalized_text": normalized,
            "answer_id": None,
            "cached": False
        }
    
    def get_cached_answer(self, question_hash: str) -> Optional[dict]:
        """
        Obtiene una respuesta cacheada por su hash
        
        Args:
            question_hash: Hash SHA256 de la pregunta normalizada
            
        Returns:
            dict | None: Respuesta si existe, None si no
        """
        return self.ai_answers_repo.get_by_hash(question_hash)
    
    def check_if_cached(self, question_text: str) -> bool:
        """
        Verifica si una pregunta ya tiene respuesta en cache
        
        Args:
            question_text: Texto de la pregunta
            
        Returns:
            bool: True si existe en cache
        """
        normalized = normalize_text(question_text)
        question_hash = generate_hash(normalized)
        cached = self.ai_answers_repo.get_by_hash(question_hash)
        return cached is not None
