"""
Tests unitarios para AIService
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from app.services.ai_service import AIService, AIResponseError, JSONParseError


class TestBuildPrompt:
    """Tests para build_prompt()"""
    
    def test_build_prompt_basic(self):
        """Test: Construye prompt básico sin contexto"""
        service = AIService(api_key="test-key")
        
        result = service.build_prompt("¿Qué es la energía cinética?")
        
        assert "system" in result
        assert "user" in result
        assert "tutor experto" in result["system"]
        assert "JSON" in result["system"]
        assert "¿Qué es la energía cinética?" in result["user"]
    
    def test_build_prompt_with_context(self):
        """Test: Incluye contexto en el prompt"""
        service = AIService(api_key="test-key")
        
        context = {
            "subject": "física",
            "difficulty": "medium",
            "previous_questions": ["¿Qué es la energía?"]
        }
        
        result = service.build_prompt("¿Qué es la energía cinética?", context)
        
        assert "física" in result["user"]
        assert "medium" in result["user"]
        assert "¿Qué es la energía?" in result["user"]
    
    def test_build_prompt_structure(self):
        """Test: Prompt especifica estructura JSON correcta"""
        service = AIService(api_key="test-key")
        
        result = service.build_prompt("test question")
        
        assert "steps" in result["system"]
        assert "total_duration" in result["system"]
        assert "title" in result["system"]
        assert "type" in result["system"]
        assert "content" in result["system"]
    
    def test_build_prompt_specifies_types(self):
        """Test: Prompt especifica tipos de paso disponibles"""
        service = AIService(api_key="test-key")
        
        result = service.build_prompt("test")
        
        assert "text" in result["system"]
        assert "math" in result["system"]
        assert "image" in result["system"]


class TestGenerateAnswer:
    """Tests para generate_answer()"""
    
    @patch('app.services.ai_service.OpenAI')
    def test_generate_answer_success(self, mock_openai_class):
        """Test: Genera respuesta exitosamente"""
        # Arrange
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        valid_response = {
            "steps": [
                {
                    "title": "Definición",
                    "type": "text",
                    "content": "La energía cinética es...",
                    "canvas_commands": []
                }
            ],
            "total_duration": 60
        }
        
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = json.dumps(valid_response)
        mock_client.chat.completions.create.return_value = mock_completion
        
        service = AIService(api_key="test-key")
        
        # Act
        result = service.generate_answer("¿Qué es la energía cinética?")
        
        # Assert
        assert result["steps"][0]["title"] == "Definición"
        assert result["total_duration"] == 60
        assert len(result["steps"]) == 1
    
    @patch('app.services.ai_service.OpenAI')
    def test_generate_answer_with_context(self, mock_openai_class):
        """Test: Genera respuesta con contexto"""
        # Arrange
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        valid_response = {
            "steps": [{"title": "Test", "type": "text", "content": "Content"}],
            "total_duration": 30
        }
        
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = json.dumps(valid_response)
        mock_client.chat.completions.create.return_value = mock_completion
        
        service = AIService(api_key="test-key")
        context = {"subject": "física"}
        
        # Act
        result = service.generate_answer("test", context)
        
        # Assert
        assert result is not None
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('app.services.ai_service.OpenAI')
    def test_generate_answer_retry_on_json_error(self, mock_openai_class):
        """Test: Reintenta cuando falla el parsing de JSON"""
        # Arrange
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        valid_response = {
            "steps": [{"title": "Test", "type": "text", "content": "Content"}],
            "total_duration": 30
        }
        
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        
        # Primera llamada: JSON inválido
        # Segunda llamada: JSON válido
        mock_completion.choices[0].message.content = json.dumps(valid_response)
        mock_client.chat.completions.create.side_effect = [
            Mock(choices=[Mock(message=Mock(content="invalid json {"))]),
            mock_completion
        ]
        
        service = AIService(api_key="test-key")
        
        # Act
        result = service.generate_answer("test")
        
        # Assert
        assert result is not None
        assert mock_client.chat.completions.create.call_count == 2
    
    @patch('app.services.ai_service.OpenAI')
    def test_generate_answer_fails_after_retries(self, mock_openai_class):
        """Test: Falla después de agotar reintentos"""
        # Arrange
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = "invalid json"
        mock_client.chat.completions.create.return_value = mock_completion
        
        service = AIService(api_key="test-key")
        
        # Act & Assert
        with pytest.raises(JSONParseError) as exc_info:
            service.generate_answer("test")
        
        assert "intentos" in str(exc_info.value)
        assert mock_client.chat.completions.create.call_count == 3  # 1 + 2 reintentos
    
    @patch('app.services.ai_service.OpenAI')
    def test_generate_answer_openai_error(self, mock_openai_class):
        """Test: Maneja errores de OpenAI"""
        # Arrange
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        service = AIService(api_key="test-key")
        
        # Act & Assert
        with pytest.raises(AIResponseError) as exc_info:
            service.generate_answer("test")
        
        assert "API Error" in str(exc_info.value)


class TestParseJSONResponse:
    """Tests para _parse_json_response()"""
    
    def test_parse_valid_json(self):
        """Test: Parsea JSON válido"""
        service = AIService(api_key="test-key")
        
        valid_json = '{"steps": [], "total_duration": 60}'
        result = service._parse_json_response(valid_json)
        
        assert result["steps"] == []
        assert result["total_duration"] == 60
    
    def test_parse_json_with_extra_text(self):
        """Test: Parsea JSON con texto extra"""
        service = AIService(api_key="test-key")
        
        response = 'Aquí está el JSON: {"steps": [], "total_duration": 60} Espero que ayude'
        result = service._parse_json_response(response)
        
        assert result["steps"] == []
    
    def test_parse_json_with_markdown(self):
        """Test: Parsea JSON dentro de markdown"""
        service = AIService(api_key="test-key")
        
        response = '```json\n{"steps": [], "total_duration": 60}\n```'
        result = service._parse_json_response(response)
        
        assert result["steps"] == []
    
    def test_parse_invalid_json_raises_error(self):
        """Test: JSON inválido lanza error"""
        service = AIService(api_key="test-key")
        
        with pytest.raises(JSONParseError):
            service._parse_json_response("not json at all")


class TestValidateResponseStructure:
    """Tests para _validate_response_structure()"""
    
    def test_validate_valid_structure(self):
        """Test: Estructura válida pasa validación"""
        service = AIService(api_key="test-key")
        
        valid_response = {
            "steps": [
                {
                    "title": "Paso 1",
                    "type": "text",
                    "content": "Contenido",
                    "canvas_commands": []
                }
            ],
            "total_duration": 60
        }
        
        # No debe lanzar excepción
        service._validate_response_structure(valid_response)
    
    def test_validate_missing_steps_raises_error(self):
        """Test: Falta campo 'steps'"""
        service = AIService(api_key="test-key")
        
        with pytest.raises(JSONParseError) as exc_info:
            service._validate_response_structure({"total_duration": 60})
        
        assert "steps" in str(exc_info.value)
    
    def test_validate_empty_steps_raises_error(self):
        """Test: Array 'steps' vacío"""
        service = AIService(api_key="test-key")
        
        with pytest.raises(JSONParseError) as exc_info:
            service._validate_response_structure({
                "steps": [],
                "total_duration": 60
            })
        
        assert "vacío" in str(exc_info.value)
    
    def test_validate_missing_step_field_raises_error(self):
        """Test: Step sin campo requerido"""
        service = AIService(api_key="test-key")
        
        with pytest.raises(JSONParseError) as exc_info:
            service._validate_response_structure({
                "steps": [{"title": "Test", "type": "text"}],  # Falta 'content'
                "total_duration": 60
            })
        
        assert "content" in str(exc_info.value)
    
    def test_validate_invalid_step_type_raises_error(self):
        """Test: Step con type inválido"""
        service = AIService(api_key="test-key")
        
        with pytest.raises(JSONParseError) as exc_info:
            service._validate_response_structure({
                "steps": [{
                    "title": "Test",
                    "type": "invalid_type",
                    "content": "Content"
                }],
                "total_duration": 60
            })
        
        assert "type inválido" in str(exc_info.value)
    
    def test_validate_missing_total_duration_raises_error(self):
        """Test: Falta 'total_duration'"""
        service = AIService(api_key="test-key")
        
        with pytest.raises(JSONParseError) as exc_info:
            service._validate_response_structure({
                "steps": [{
                    "title": "Test",
                    "type": "text",
                    "content": "Content"
                }]
            })
        
        assert "total_duration" in str(exc_info.value)
    
    def test_validate_invalid_total_duration_type(self):
        """Test: total_duration no es número"""
        service = AIService(api_key="test-key")
        
        with pytest.raises(JSONParseError) as exc_info:
            service._validate_response_structure({
                "steps": [{
                    "title": "Test",
                    "type": "text",
                    "content": "Content"
                }],
                "total_duration": "not a number"
            })
        
        assert "número" in str(exc_info.value)
    
    def test_validate_multiple_steps(self):
        """Test: Valida múltiples steps correctamente"""
        service = AIService(api_key="test-key")
        
        valid_response = {
            "steps": [
                {"title": "Paso 1", "type": "text", "content": "Content 1"},
                {"title": "Paso 2", "type": "math", "content": "E=mc^2"},
                {"title": "Paso 3", "type": "image", "content": "Diagrama"}
            ],
            "total_duration": 120
        }
        
        # No debe lanzar excepción
        service._validate_response_structure(valid_response)


class TestAttemptJSONRepair:
    """Tests para _attempt_json_repair()"""
    
    def test_repair_removes_prefix_text(self):
        """Test: Quita texto antes del JSON"""
        service = AIService(api_key="test-key")
        
        response = 'Aquí está: {"key": "value"}'
        repaired = service._attempt_json_repair(response)
        
        assert repaired == '{"key": "value"}'
    
    def test_repair_removes_suffix_text(self):
        """Test: Quita texto después del JSON"""
        service = AIService(api_key="test-key")
        
        response = '{"key": "value"} Espero que ayude'
        repaired = service._attempt_json_repair(response)
        
        assert repaired == '{"key": "value"}'
    
    def test_repair_removes_markdown(self):
        """Test: Quita markdown code blocks"""
        service = AIService(api_key="test-key")
        
        response = '```json\n{"key": "value"}\n```'
        repaired = service._attempt_json_repair(response)
        
        assert '```' not in repaired
        assert '{"key": "value"}' in repaired
    
    def test_repair_strips_whitespace(self):
        """Test: Quita espacios en blanco"""
        service = AIService(api_key="test-key")
        
        response = '  \n  {"key": "value"}  \n  '
        repaired = service._attempt_json_repair(response)
        
        assert repaired == '{"key": "value"}'


class TestIntegration:
    """Tests de integración para flujos completos"""
    
    @patch('app.services.ai_service.OpenAI')
    def test_full_flow_success(self, mock_openai_class):
        """Test: Flujo completo exitoso"""
        # Arrange
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        response_data = {
            "steps": [
                {
                    "title": "Definición de energía cinética",
                    "type": "text",
                    "content": "La energía cinética es la energía que posee un objeto debido a su movimiento.",
                    "canvas_commands": []
                },
                {
                    "title": "Fórmula matemática",
                    "type": "math",
                    "content": "E_c = \\frac{1}{2}mv^2",
                    "canvas_commands": []
                }
            ],
            "total_duration": 90
        }
        
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = json.dumps(response_data)
        mock_client.chat.completions.create.return_value = mock_completion
        
        service = AIService(api_key="test-key")
        
        # Act
        result = service.generate_answer(
            "¿Qué es la energía cinética?",
            {"subject": "física", "difficulty": "medium"}
        )
        
        # Assert
        assert len(result["steps"]) == 2
        assert result["steps"][0]["type"] == "text"
        assert result["steps"][1]["type"] == "math"
        assert result["total_duration"] == 90
        
        # Verificar que se llamó a OpenAI correctamente
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "gpt-4"
        assert call_args[1]["temperature"] == 0.7
        assert len(call_args[1]["messages"]) == 2
    
    def test_initialization_without_api_key_raises_error(self):
        """Test: Inicialización sin API key lanza error"""
        with patch.dict('os.environ', {}, clear=True):
            with patch('app.services.ai_service.Config') as mock_config:
                mock_config.OPENAI_API_KEY = None
                
                with pytest.raises(ValueError) as exc_info:
                    AIService()
                
                assert "OPENAI_API_KEY" in str(exc_info.value)
