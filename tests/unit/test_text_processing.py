"""
Tests para utilidades de procesamiento de texto
"""
import pytest
from app.utils.text_processing import normalize_text, generate_hash, truncate_text


def test_normalize_text():
    """Test de normalización de texto"""
    assert normalize_text("¿Qué es Python?") == "que es python"
    assert normalize_text("  Múltiples   espacios  ") == "multiples espacios"
    assert normalize_text("MAYÚSCULAS") == "mayusculas"


def test_generate_hash():
    """Test de generación de hash"""
    text = "test"
    hash1 = generate_hash(text)
    hash2 = generate_hash(text)
    
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 produce 64 caracteres hex


def test_truncate_text():
    """Test de truncado de texto"""
    text = "Este es un texto muy largo que necesita ser truncado"
    
    truncated = truncate_text(text, max_length=20)
    assert len(truncated) <= 20
    assert truncated.endswith("...")
    
    short_text = "Corto"
    assert truncate_text(short_text, max_length=20) == short_text
