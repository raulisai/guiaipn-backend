"""
Utilidades de procesamiento de texto
"""
import hashlib
import re
from unidecode import unidecode


def normalize_text(text: str) -> str:
    """
    Normaliza texto para generar hashes consistentes
    
    Args:
        text: Texto a normalizar
        
    Returns:
        str: Texto normalizado
    """
    # Lowercase
    text = text.lower()
    
    # Quitar acentos
    text = unidecode(text)
    
    # Quitar puntuación extra (mantener solo letras, números y espacios)
    text = re.sub(r'[^\w\s]', '', text)
    
    # Normalizar espacios múltiples a uno solo
    text = re.sub(r'\s+', ' ', text)
    
    # Trim
    text = text.strip()
    
    return text


def generate_hash(text: str) -> str:
    """
    Genera un hash SHA256 de un texto
    
    Args:
        text: Texto a hashear
        
    Returns:
        str: Hash en hexadecimal
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Trunca un texto a una longitud máxima
    
    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        suffix: Sufijo a agregar si se trunca
        
    Returns:
        str: Texto truncado
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
