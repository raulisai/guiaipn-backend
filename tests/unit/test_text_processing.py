"""
Tests para utilidades de procesamiento de texto
"""
import pytest
from app.utils.text_processing import normalize_text, generate_hash, truncate_text


class TestNormalizeText:
    """Tests para normalize_text()"""
    
    def test_normalize_basic(self):
        """Test: Normalización básica"""
        text = "¿Cuál es la fórmula de la energía?"
        normalized = normalize_text(text)
        
        assert normalized == "cual es la formula de la energia"
        assert " " in normalized
        assert "á" not in normalized
        assert "¿" not in normalized
        assert "?" not in normalized
    
    def test_normalize_removes_accents(self):
        """Test: Quita acentos correctamente"""
        text = "Matemáticas, física, química"
        normalized = normalize_text(text)
        
        assert normalized == "matematicas fisica quimica"
        assert "á" not in normalized
        assert "í" not in normalized
    
    def test_normalize_lowercase(self):
        """Test: Convierte a minúsculas"""
        text = "PREGUNTA EN MAYÚSCULAS"
        normalized = normalize_text(text)
        
        assert normalized == "pregunta en mayusculas"
        assert normalized.islower()
    
    def test_normalize_removes_punctuation(self):
        """Test: Quita puntuación"""
        text = "¿Qué es esto? ¡Es una prueba!"
        normalized = normalize_text(text)
        
        assert normalized == "que es esto es una prueba"
        assert "¿" not in normalized
        assert "?" not in normalized
        assert "!" not in normalized
    
    def test_normalize_collapses_spaces(self):
        """Test: Colapsa espacios múltiples"""
        text = "texto    con     muchos      espacios"
        normalized = normalize_text(text)
        
        assert normalized == "texto con muchos espacios"
        assert "  " not in normalized
    
    def test_normalize_trims_whitespace(self):
        """Test: Quita espacios al inicio y final"""
        text = "   texto con espacios   "
        normalized = normalize_text(text)
        
        assert normalized == "texto con espacios"
        assert not normalized.startswith(" ")
        assert not normalized.endswith(" ")
    
    def test_normalize_empty_string(self):
        """Test: String vacío retorna vacío"""
        assert normalize_text("") == ""
        assert normalize_text("   ") == ""
    
    def test_normalize_special_characters(self):
        """Test: Maneja caracteres especiales"""
        text = "x² + y³ = z⁴"
        normalized = normalize_text(text)
        
        # Debe quitar superíndices y símbolos
        assert "²" not in normalized
        assert "³" not in normalized
        assert "+" not in normalized
        assert "=" not in normalized
    
    def test_normalize_numbers_preserved(self):
        """Test: Números se preservan"""
        text = "La respuesta es 42"
        normalized = normalize_text(text)
        
        assert "42" in normalized
        assert normalized == "la respuesta es 42"


class TestGenerateHash:
    """Tests para generate_hash()"""
    
    def test_generate_hash_basic(self):
        """Test: Generación básica de hash"""
        text = "pregunta de prueba"
        hash1 = generate_hash(text)
        hash2 = generate_hash(text)
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 = 64 caracteres hex
    
    def test_generate_hash_deterministic(self):
        """Test: Hash es determinístico"""
        text = "misma pregunta"
        
        hashes = [generate_hash(text) for _ in range(10)]
        
        assert len(set(hashes)) == 1  # Todos iguales
    
    def test_generate_hash_different_inputs(self):
        """Test: Inputs diferentes generan hashes diferentes"""
        hash1 = generate_hash("pregunta 1")
        hash2 = generate_hash("pregunta 2")
        
        assert hash1 != hash2
    
    def test_generate_hash_case_sensitive(self):
        """Test: Hash es case-sensitive"""
        hash1 = generate_hash("Pregunta")
        hash2 = generate_hash("pregunta")
        
        assert hash1 != hash2
    
    def test_generate_hash_whitespace_sensitive(self):
        """Test: Hash es sensible a espacios"""
        hash1 = generate_hash("pregunta")
        hash2 = generate_hash("pregunta ")
        hash3 = generate_hash(" pregunta")
        
        assert hash1 != hash2
        assert hash1 != hash3
    
    def test_generate_hash_empty_string(self):
        """Test: String vacío genera hash válido"""
        hash_empty = generate_hash("")
        
        assert len(hash_empty) == 64
        assert hash_empty == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    
    def test_generate_hash_unicode(self):
        """Test: Maneja caracteres Unicode"""
        text = "¿Qué es π?"
        hash_result = generate_hash(text)
        
        assert len(hash_result) == 64
        assert isinstance(hash_result, str)


class TestTruncateText:
    """Tests para truncate_text()"""
    
    def test_truncate_basic(self):
        """Test: Truncado básico"""
        text = "Este es un texto muy largo que necesita ser truncado"
        truncated = truncate_text(text, max_length=20)
        
        assert len(truncated) <= 20
        assert truncated.endswith("...")
    
    def test_truncate_short_text(self):
        """Test: Texto corto no se trunca"""
        text = "Texto corto"
        truncated = truncate_text(text, max_length=100)
        
        assert truncated == text
        assert not truncated.endswith("...")
    
    def test_truncate_exact_length(self):
        """Test: Texto de longitud exacta no se trunca"""
        text = "12345"
        truncated = truncate_text(text, max_length=5)
        
        assert truncated == text
    
    def test_truncate_custom_suffix(self):
        """Test: Sufijo personalizado"""
        text = "Texto largo para truncar"
        truncated = truncate_text(text, max_length=15, suffix="[...]")
        
        assert len(truncated) <= 15
        assert truncated.endswith("[...]")
    
    def test_truncate_no_suffix(self):
        """Test: Sin sufijo"""
        text = "Texto largo para truncar"
        truncated = truncate_text(text, max_length=10, suffix="")
        
        assert len(truncated) == 10
        assert not truncated.endswith("...")


class TestIntegration:
    """Tests de integración para flujos completos"""
    
    def test_normalize_then_hash(self):
        """Test: Normalizar y luego hashear produce resultados consistentes"""
        questions = [
            "¿Cuál es la fórmula de Einstein?",
            "Cual es la formula de Einstein",
            "  CUAL ES LA FORMULA DE EINSTEIN  "
        ]
        
        hashes = [generate_hash(normalize_text(q)) for q in questions]
        
        # Todas las variaciones deben producir el mismo hash
        assert len(set(hashes)) == 1
    
    def test_full_question_processing_pipeline(self):
        """Test: Pipeline completo de procesamiento"""
        original = "¿Qué es la energía cinética?"
        
        # 1. Normalizar
        normalized = normalize_text(original)
        assert normalized == "que es la energia cinetica"
        
        # 2. Generar hash
        hash_result = generate_hash(normalized)
        assert len(hash_result) == 64
        
        # 3. Truncar para display
        truncated = truncate_text(original, max_length=20)
        assert len(truncated) <= 20
    
    def test_short_text(self):
        """Test: Texto corto no se trunca"""
        short_text = "Corto"
        assert truncate_text(short_text, max_length=20) == short_text
