"""
Tests unitarios para autenticación con Supabase
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.auth.supabase import verify_token
from app.auth.decorators import require_auth, require_auth_socket


class TestVerifyToken:
    """Tests para la función verify_token"""
    
    @patch('app.auth.supabase.get_supabase')
    def test_verify_token_success(self, mock_get_supabase):
        """Test: Token válido retorna información del usuario"""
        # Arrange
        mock_supabase = Mock()
        mock_get_supabase.return_value = mock_supabase
        
        mock_user = Mock()
        mock_user.id = "user-123"
        mock_user.email = "test@example.com"
        mock_user.user_metadata = {"name": "Test User"}
        
        mock_response = Mock()
        mock_response.user = mock_user
        
        mock_supabase.auth.get_user.return_value = mock_response
        
        # Act
        result = verify_token("valid-token")
        
        # Assert
        assert result["id"] == "user-123"
        assert result["email"] == "test@example.com"
        assert result["user_metadata"]["name"] == "Test User"
        mock_supabase.auth.get_user.assert_called_once_with("valid-token")
    
    @patch('app.auth.supabase.get_supabase')
    def test_verify_token_invalid(self, mock_get_supabase):
        """Test: Token inválido lanza excepción"""
        # Arrange
        mock_supabase = Mock()
        mock_get_supabase.return_value = mock_supabase
        
        mock_response = Mock()
        mock_response.user = None
        
        mock_supabase.auth.get_user.return_value = mock_response
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            verify_token("invalid-token")
        
        assert "Token inválido" in str(exc_info.value)
    
    @patch('app.auth.supabase.get_supabase')
    def test_verify_token_supabase_error(self, mock_get_supabase):
        """Test: Error de Supabase se propaga correctamente"""
        # Arrange
        mock_supabase = Mock()
        mock_get_supabase.return_value = mock_supabase
        mock_supabase.auth.get_user.side_effect = Exception("Supabase error")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            verify_token("token")
        
        assert "Error verificando token" in str(exc_info.value)


class TestRequireAuthDecorator:
    """Tests para el decorador @require_auth (HTTP)"""
    
    def test_require_auth_decorator_exists(self):
        """Test: El decorador @require_auth existe y es callable"""
        assert callable(require_auth)
        
        @require_auth
        def test_func():
            return "test"
        
        assert callable(test_func)
        assert hasattr(test_func, '__wrapped__')
        
    def test_require_auth_decorator_structure(self):
        """Test: El decorador tiene la estructura correcta"""
        import inspect
        
        # Verificar que el decorador acepta una función
        assert callable(require_auth)
        
        # Verificar que retorna un decorador
        @require_auth
        def dummy():
            pass
        
        # Verificar que preserva el nombre de la función
        assert dummy.__name__ == 'dummy'


class TestRequireAuthSocketDecorator:
    """Tests para el decorador @require_auth_socket (Socket.IO)"""
    
    @patch('app.auth.decorators.verify_token')
    @patch('app.auth.decorators.emit')
    def test_require_auth_socket_success(self, mock_emit, mock_verify_token):
        """Test: Evento con token válido pasa la autenticación"""
        # Arrange
        mock_verify_token.return_value = {
            "id": "user-123",
            "email": "test@example.com"
        }
        
        @require_auth_socket
        def socket_handler(data):
            return {"message": "success", "user": data["user"]}
        
        # Act
        data = {"token": "valid-token", "question": "test"}
        result = socket_handler(data)
        
        # Assert
        assert result["message"] == "success"
        assert result["user"]["id"] == "user-123"
        assert data["user"]["id"] == "user-123"
        mock_verify_token.assert_called_once_with("valid-token")
        mock_emit.assert_not_called()
    
    @patch('app.auth.decorators.emit')
    @patch('app.auth.decorators.disconnect')
    def test_require_auth_socket_no_token(self, mock_disconnect, mock_emit):
        """Test: Evento sin token emite error y desconecta"""
        # Arrange
        @require_auth_socket
        def socket_handler(data):
            return {"message": "success"}
        
        # Act
        data = {"question": "test"}
        result = socket_handler(data)
        
        # Assert
        assert result is None
        mock_emit.assert_called_once()
        call_args = mock_emit.call_args[0]
        assert call_args[0] == "error"
        assert call_args[1]["code"] == "AUTH_REQUIRED"
        mock_disconnect.assert_called_once()
    
    @patch('app.auth.decorators.verify_token')
    @patch('app.auth.decorators.emit')
    @patch('app.auth.decorators.disconnect')
    def test_require_auth_socket_invalid_token(self, mock_disconnect, mock_emit, mock_verify_token):
        """Test: Token inválido emite error y desconecta"""
        # Arrange
        mock_verify_token.side_effect = Exception("Token inválido")
        
        @require_auth_socket
        def socket_handler(data):
            return {"message": "success"}
        
        # Act
        data = {"token": "invalid-token"}
        result = socket_handler(data)
        
        # Assert
        assert result is None
        mock_emit.assert_called_once()
        call_args = mock_emit.call_args[0]
        assert call_args[0] == "error"
        assert call_args[1]["code"] == "AUTH_FAILED"
        mock_disconnect.assert_called_once()
    
    @patch('app.auth.decorators.emit')
    def test_require_auth_socket_invalid_payload(self, mock_emit):
        """Test: Payload no-dict emite error"""
        # Arrange
        @require_auth_socket
        def socket_handler(data):
            return {"message": "success"}
        
        # Act
        result = socket_handler("not-a-dict")
        
        # Assert
        assert result is None
        mock_emit.assert_called_once()
        call_args = mock_emit.call_args[0]
        assert call_args[0] == "error"
        assert call_args[1]["code"] == "INVALID_PAYLOAD"
    
    @patch('app.auth.decorators.emit')
    @patch('app.auth.decorators.disconnect')
    def test_require_auth_socket_empty_data(self, mock_disconnect, mock_emit):
        """Test: Evento sin data emite error"""
        # Arrange
        @require_auth_socket
        def socket_handler(data):
            return {"message": "success"}
        
        # Act
        result = socket_handler({})
        
        # Assert
        assert result is None
        mock_emit.assert_called_once()
        call_args = mock_emit.call_args[0]
        assert call_args[0] == "error"
        assert call_args[1]["code"] == "AUTH_REQUIRED"
        mock_disconnect.assert_called_once()


class TestIntegration:
    """Tests de integración para flujos completos"""
    
    @patch('app.auth.supabase.get_supabase')
    @patch('app.auth.decorators.emit')
    def test_full_socket_auth_flow(self, mock_emit, mock_get_supabase):
        """Test: Flujo completo de autenticación en Socket.IO"""
        # Arrange
        mock_supabase = Mock()
        mock_get_supabase.return_value = mock_supabase
        
        mock_user = Mock()
        mock_user.id = "user-123"
        mock_user.email = "test@example.com"
        mock_user.user_metadata = {}
        
        mock_response = Mock()
        mock_response.user = mock_user
        
        mock_supabase.auth.get_user.return_value = mock_response
        
        @require_auth_socket
        def handle_question(data):
            return {
                "answer": "processed",
                "user_id": data["user"]["id"]
            }
        
        # Act
        data = {"token": "valid-token", "question": "¿Qué es Python?"}
        result = handle_question(data)
        
        # Assert
        assert result["answer"] == "processed"
        assert result["user_id"] == "user-123"
        assert data["user"]["email"] == "test@example.com"
        mock_emit.assert_not_called()
