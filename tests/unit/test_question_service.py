"""
Tests unitarios para QuestionService
"""
import pytest
from unittest.mock import Mock, MagicMock
from app.services.question_service import QuestionService, QuestionValidationError


class TestQuestionValidation:
    """Tests para validate_question()"""
    
    def test_validate_valid_question(self):
        """Test: Pregunta válida pasa validación"""
        service = QuestionService(ai_answers_repo=Mock())
        
        # No debe lanzar excepción
        service.validate_question("¿Qué es la energía cinética?")
    
    def test_validate_empty_string_raises_error(self):
        """Test: String vacío lanza error"""
        service = QuestionService(ai_answers_repo=Mock())
        
        with pytest.raises(QuestionValidationError) as exc_info:
            service.validate_question("")
        
        assert "no vacío" in str(exc_info.value)
    
    def test_validate_none_raises_error(self):
        """Test: None lanza error"""
        service = QuestionService(ai_answers_repo=Mock())
        
        with pytest.raises(QuestionValidationError):
            service.validate_question(None)
    
    def test_validate_non_string_raises_error(self):
        """Test: No-string lanza error"""
        service = QuestionService(ai_answers_repo=Mock())
        
        with pytest.raises(QuestionValidationError):
            service.validate_question(123)
    
    def test_validate_too_short_raises_error(self):
        """Test: Pregunta muy corta lanza error"""
        service = QuestionService(ai_answers_repo=Mock())
        
        with pytest.raises(QuestionValidationError) as exc_info:
            service.validate_question("abc")
        
        assert "al menos" in str(exc_info.value)
    
    def test_validate_too_long_raises_error(self):
        """Test: Pregunta muy larga lanza error"""
        service = QuestionService(ai_answers_repo=Mock())
        long_question = "a" * 1001
        
        with pytest.raises(QuestionValidationError) as exc_info:
            service.validate_question(long_question)
        
        assert "exceder" in str(exc_info.value)
    
    def test_validate_minimum_length(self):
        """Test: Pregunta de longitud mínima es válida"""
        service = QuestionService(ai_answers_repo=Mock())
        
        # 5 caracteres es el mínimo
        service.validate_question("12345")
    
    def test_validate_maximum_length(self):
        """Test: Pregunta de longitud máxima es válida"""
        service = QuestionService(ai_answers_repo=Mock())
        
        # 1000 caracteres es el máximo
        max_question = "a" * 1000
        service.validate_question(max_question)
    
    def test_validate_whitespace_only_raises_error(self):
        """Test: Solo espacios lanza error"""
        service = QuestionService(ai_answers_repo=Mock())
        
        with pytest.raises(QuestionValidationError):
            service.validate_question("     ")


class TestProcessQuestion:
    """Tests para process_question()"""
    
    def test_process_question_cached(self):
        """Test: Pregunta en cache retorna answer_id"""
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_hash.return_value = {
            "id": "answer-uuid-123",
            "answer_steps": [{"step": 1, "text": "Paso 1"}],
            "total_duration": 60
        }
        mock_repo.increment_usage = Mock()
        
        service = QuestionService(ai_answers_repo=mock_repo)
        
        # Act
        result = service.process_question("user-123", "¿Qué es la energía?")
        
        # Assert
        assert result["cached"] is True
        assert result["answer_id"] == "answer-uuid-123"
        assert result["question_hash"] is not None
        assert result["normalized_text"] == "que es la energia"
        assert "answer_steps" in result
        mock_repo.increment_usage.assert_called_once_with("answer-uuid-123")
    
    def test_process_question_not_cached(self):
        """Test: Pregunta no en cache retorna None"""
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_hash.return_value = None
        
        service = QuestionService(ai_answers_repo=mock_repo)
        
        # Act
        result = service.process_question("user-123", "¿Qué es la física cuántica?")
        
        # Assert
        assert result["cached"] is False
        assert result["answer_id"] is None
        assert result["question_hash"] is not None
        assert result["normalized_text"] == "que es la fisica cuantica"
    
    def test_process_question_normalizes_text(self):
        """Test: Normaliza texto correctamente"""
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_hash.return_value = None
        
        service = QuestionService(ai_answers_repo=mock_repo)
        
        # Act
        result = service.process_question("user-123", "¿CUÁL ES LA FÓRMULA?")
        
        # Assert
        assert result["normalized_text"] == "cual es la formula"
        assert result["question_text"] == "¿CUÁL ES LA FÓRMULA?"
    
    def test_process_question_generates_consistent_hash(self):
        """Test: Genera hash consistente para misma pregunta"""
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_hash.return_value = None
        
        service = QuestionService(ai_answers_repo=mock_repo)
        
        # Act
        result1 = service.process_question("user-123", "¿Qué es energía?")
        result2 = service.process_question("user-123", "Que es energia")
        
        # Assert
        assert result1["question_hash"] == result2["question_hash"]
    
    def test_process_question_invalid_raises_error(self):
        """Test: Pregunta inválida lanza error"""
        # Arrange
        service = QuestionService(ai_answers_repo=Mock())
        
        # Act & Assert
        with pytest.raises(QuestionValidationError):
            service.process_question("user-123", "")
    
    def test_process_question_preserves_original(self):
        """Test: Preserva texto original"""
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_hash.return_value = None
        
        service = QuestionService(ai_answers_repo=mock_repo)
        original = "¿Cuál es la fórmula de Einstein?"
        
        # Act
        result = service.process_question("user-123", original)
        
        # Assert
        assert result["question_text"] == original
        assert result["normalized_text"] != original


class TestGetCachedAnswer:
    """Tests para get_cached_answer()"""
    
    def test_get_cached_answer_exists(self):
        """Test: Obtiene respuesta cacheada"""
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_hash.return_value = {
            "id": "answer-123",
            "answer_steps": []
        }
        
        service = QuestionService(ai_answers_repo=mock_repo)
        
        # Act
        result = service.get_cached_answer("hash123")
        
        # Assert
        assert result is not None
        assert result["id"] == "answer-123"
        mock_repo.get_by_hash.assert_called_once_with("hash123")
    
    def test_get_cached_answer_not_exists(self):
        """Test: Respuesta no existe retorna None"""
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_hash.return_value = None
        
        service = QuestionService(ai_answers_repo=mock_repo)
        
        # Act
        result = service.get_cached_answer("hash456")
        
        # Assert
        assert result is None


class TestCheckIfCached:
    """Tests para check_if_cached()"""
    
    def test_check_if_cached_true(self):
        """Test: Pregunta en cache retorna True"""
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_hash.return_value = {"id": "answer-123"}
        
        service = QuestionService(ai_answers_repo=mock_repo)
        
        # Act
        result = service.check_if_cached("¿Qué es la energía?")
        
        # Assert
        assert result is True
    
    def test_check_if_cached_false(self):
        """Test: Pregunta no en cache retorna False"""
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_hash.return_value = None
        
        service = QuestionService(ai_answers_repo=mock_repo)
        
        # Act
        result = service.check_if_cached("¿Qué es la física cuántica?")
        
        # Assert
        assert result is False
    
    def test_check_if_cached_normalizes(self):
        """Test: Normaliza antes de buscar"""
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_hash.return_value = {"id": "answer-123"}
        
        service = QuestionService(ai_answers_repo=mock_repo)
        
        # Act
        result1 = service.check_if_cached("¿Qué es energía?")
        result2 = service.check_if_cached("QUE ES ENERGIA")
        
        # Assert
        assert result1 is True
        assert result2 is True
        # Debe llamar con el mismo hash
        calls = mock_repo.get_by_hash.call_args_list
        assert calls[0][0][0] == calls[1][0][0]


class TestIntegration:
    """Tests de integración para flujos completos"""
    
    def test_full_question_flow_cached(self):
        """Test: Flujo completo con pregunta cacheada"""
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_hash.return_value = {
            "id": "answer-uuid-123",
            "question_hash": "hash123",
            "answer_steps": [
                {"step": 1, "text": "Paso 1"},
                {"step": 2, "text": "Paso 2"}
            ],
            "total_duration": 120
        }
        mock_repo.increment_usage = Mock()
        
        service = QuestionService(ai_answers_repo=mock_repo)
        
        # Act
        result = service.process_question(
            user_id="user-456",
            question_text="¿Cuál es la fórmula de la energía cinética?"
        )
        
        # Assert
        assert result["cached"] is True
        assert result["answer_id"] == "answer-uuid-123"
        assert len(result["answer_steps"]) == 2
        assert result["total_duration"] == 120
        mock_repo.increment_usage.assert_called_once()
    
    def test_full_question_flow_not_cached(self):
        """Test: Flujo completo con pregunta nueva"""
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_hash.return_value = None
        
        service = QuestionService(ai_answers_repo=mock_repo)
        
        # Act
        result = service.process_question(
            user_id="user-789",
            question_text="¿Qué es la mecánica cuántica?"
        )
        
        # Assert
        assert result["cached"] is False
        assert result["answer_id"] is None
        assert result["question_hash"] is not None
        assert len(result["question_hash"]) == 64  # SHA256
    
    def test_same_question_different_formats(self):
        """Test: Misma pregunta en diferentes formatos genera mismo hash"""
        # Arrange
        mock_repo = Mock()
        mock_repo.get_by_hash.return_value = None
        
        service = QuestionService(ai_answers_repo=mock_repo)
        
        questions = [
            "¿Qué es la energía?",
            "Que es la energia",
            "  QUE ES LA ENERGIA  ",
            "¿QUÉ ES LA ENERGÍA?"
        ]
        
        # Act
        hashes = [
            service.process_question("user-123", q)["question_hash"]
            for q in questions
        ]
        
        # Assert
        assert len(set(hashes)) == 1  # Todos producen el mismo hash
