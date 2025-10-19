"""
Validadores de datos
"""
import re


def validate_email(email: str) -> bool:
    """
    Valida formato de email
    
    Args:
        email: Email a validar
        
    Returns:
        bool: True si es válido
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_question(question: str, min_length: int = 3, max_length: int = 1000) -> tuple:
    """
    Valida una pregunta
    
    Args:
        question: Pregunta a validar
        min_length: Longitud mínima
        max_length: Longitud máxima
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not question or not question.strip():
        return False, "La pregunta no puede estar vacía"
    
    question = question.strip()
    
    if len(question) < min_length:
        return False, f"La pregunta debe tener al menos {min_length} caracteres"
    
    if len(question) > max_length:
        return False, f"La pregunta no puede exceder {max_length} caracteres"
    
    return True, None


def validate_uuid(uuid_string: str) -> bool:
    """
    Valida formato UUID
    
    Args:
        uuid_string: UUID a validar
        
    Returns:
        bool: True si es válido
    """
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(pattern, uuid_string.lower()))
