"""
Tests para validadores
"""
import pytest
from app.utils.validators import validate_email, validate_question, validate_uuid


def test_validate_email():
    """Test de validación de email"""
    assert validate_email("test@example.com") is True
    assert validate_email("user.name+tag@example.co.uk") is True
    assert validate_email("invalid-email") is False
    assert validate_email("@example.com") is False


def test_validate_question():
    """Test de validación de pregunta"""
    valid, error = validate_question("¿Qué es Python?")
    assert valid is True
    assert error is None
    
    valid, error = validate_question("")
    assert valid is False
    assert error is not None
    
    valid, error = validate_question("ab")
    assert valid is False
    
    long_text = "a" * 1001
    valid, error = validate_question(long_text)
    assert valid is False


def test_validate_uuid():
    """Test de validación de UUID"""
    assert validate_uuid("550e8400-e29b-41d4-a716-446655440000") is True
    assert validate_uuid("invalid-uuid") is False
    assert validate_uuid("550e8400-e29b-41d4-a716") is False
