"""
Tests de integración para SessionService y SessionRepository con fakeredis
"""
import pytest
import fakeredis
import time
from app.repositories.session_repository import SessionRepository
from app.services.session_service import SessionService, SessionExpiredError


@pytest.fixture
def fake_redis():
    """Fixture que proporciona un cliente Redis falso"""
    return fakeredis.FakeStrictRedis(decode_responses=True)


@pytest.fixture
def session_repo(fake_redis):
    """Fixture que proporciona un SessionRepository con Redis falso"""
    return SessionRepository(fake_redis)


@pytest.fixture
def session_service(session_repo):
    """Fixture que proporciona un SessionService con repositorio falso"""
    return SessionService(session_repo)


class TestSessionRepository:
    """Tests para SessionRepository"""
    
    def test_create_session(self, session_repo):
        """Test: Crear sesión en Redis"""
        # Arrange
        session_id = "test-session-123"
        data = {
            "user_id": "user-456",
            "current_question": None,
            "is_streaming": False
        }
        
        # Act
        result = session_repo.create(session_id, data, ttl=60)
        
        # Assert
        assert result is True
        assert session_repo.exists(session_id)
    
    def test_get_session(self, session_repo):
        """Test: Obtener sesión existente"""
        # Arrange
        session_id = "test-session-123"
        data = {"user_id": "user-456", "test": "value"}
        session_repo.create(session_id, data)
        
        # Act
        result = session_repo.get(session_id)
        
        # Assert
        assert result is not None
        assert result["user_id"] == "user-456"
        assert result["test"] == "value"
    
    def test_get_nonexistent_session(self, session_repo):
        """Test: Obtener sesión que no existe retorna None"""
        # Act
        result = session_repo.get("nonexistent-session")
        
        # Assert
        assert result is None
    
    def test_update_session(self, session_repo):
        """Test: Actualizar sesión existente"""
        # Arrange
        session_id = "test-session-123"
        initial_data = {"user_id": "user-456", "count": 0}
        session_repo.create(session_id, initial_data)
        
        # Act
        update_data = {"count": 5, "new_field": "value"}
        result = session_repo.update(session_id, update_data)
        
        # Assert
        assert result is True
        updated = session_repo.get(session_id)
        assert updated["count"] == 5
        assert updated["new_field"] == "value"
        assert updated["user_id"] == "user-456"  # Campo original preservado
    
    def test_update_nonexistent_session_raises_error(self, session_repo):
        """Test: Actualizar sesión inexistente lanza excepción"""
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            session_repo.update("nonexistent", {"data": "value"})
        
        assert "no existe" in str(exc_info.value)
    
    def test_delete_session(self, session_repo):
        """Test: Eliminar sesión"""
        # Arrange
        session_id = "test-session-123"
        session_repo.create(session_id, {"user_id": "user-456"})
        
        # Act
        result = session_repo.delete(session_id)
        
        # Assert
        assert result is True
        assert not session_repo.exists(session_id)
    
    def test_renew_ttl(self, session_repo):
        """Test: Renovar TTL de sesión"""
        # Arrange
        session_id = "test-session-123"
        session_repo.create(session_id, {"user_id": "user-456"}, ttl=10)
        
        # Act
        result = session_repo.renew_ttl(session_id, ttl=100)
        
        # Assert
        assert result is True
        ttl = session_repo.get_ttl(session_id)
        assert ttl > 10  # TTL fue renovado
    
    def test_exists(self, session_repo):
        """Test: Verificar existencia de sesión"""
        # Arrange
        session_id = "test-session-123"
        
        # Assert - No existe inicialmente
        assert not session_repo.exists(session_id)
        
        # Act - Crear sesión
        session_repo.create(session_id, {"user_id": "user-456"})
        
        # Assert - Ahora existe
        assert session_repo.exists(session_id)
    
    def test_get_ttl(self, session_repo):
        """Test: Obtener TTL de sesión"""
        # Arrange
        session_id = "test-session-123"
        session_repo.create(session_id, {"user_id": "user-456"}, ttl=60)
        
        # Act
        ttl = session_repo.get_ttl(session_id)
        
        # Assert
        assert ttl > 0
        assert ttl <= 60
    
    def test_get_all_sessions(self, session_repo):
        """Test: Obtener todas las sesiones activas"""
        # Arrange
        session_repo.create("session-1", {"user_id": "user-1"})
        session_repo.create("session-2", {"user_id": "user-2"})
        session_repo.create("session-3", {"user_id": "user-3"})
        
        # Act
        all_sessions = session_repo.get_all_sessions()
        
        # Assert
        assert len(all_sessions) == 3
        assert "session-1" in all_sessions
        assert "session-2" in all_sessions
        assert "session-3" in all_sessions


class TestSessionService:
    """Tests para SessionService"""
    
    def test_create_session(self, session_service):
        """Test: Crear sesión genera UUID y almacena datos"""
        # Act
        session_id = session_service.create_session("user-123", "socket-456")
        
        # Assert
        assert session_id is not None
        assert len(session_id) == 36  # UUID format
        assert session_service.session_exists(session_id)
        
        # Verificar datos
        session = session_service.get_session(session_id)
        assert session["user_id"] == "user-123"
        assert session["connection_id"] == "socket-456"
        assert session["is_streaming"] is False
        assert session["is_paused"] is False
    
    def test_get_session_updates_activity(self, session_service):
        """Test: Obtener sesión actualiza last_activity"""
        # Arrange
        session_id = session_service.create_session("user-123")
        original_session = session_service.repo.get(session_id)
        original_activity = original_session["last_activity"]
        
        # Wait a bit
        time.sleep(0.1)
        
        # Act
        session = session_service.get_session(session_id)
        
        # Assert
        assert session["last_activity"] > original_activity
    
    def test_get_nonexistent_session_raises_error(self, session_service):
        """Test: Obtener sesión inexistente lanza SessionExpiredError"""
        # Act & Assert
        with pytest.raises(SessionExpiredError):
            session_service.get_session("nonexistent-session")
    
    def test_update_session(self, session_service):
        """Test: Actualizar sesión modifica datos"""
        # Arrange
        session_id = session_service.create_session("user-123")
        
        # Act
        result = session_service.update_session(session_id, {
            "current_question": "hash-123",
            "is_streaming": True,
            "current_step": 5
        })
        
        # Assert
        assert result is True
        session = session_service.get_session(session_id)
        assert session["current_question"] == "hash-123"
        assert session["is_streaming"] is True
        assert session["current_step"] == 5
    
    def test_update_nonexistent_session_raises_error(self, session_service):
        """Test: Actualizar sesión inexistente lanza error"""
        # Act & Assert
        with pytest.raises(SessionExpiredError):
            session_service.update_session("nonexistent", {"data": "value"})
    
    def test_renew_ttl(self, session_service):
        """Test: Renovar TTL de sesión"""
        # Arrange
        session_id = session_service.create_session("user-123")
        
        # Act
        result = session_service.renew_ttl(session_id)
        
        # Assert
        assert result is True
        ttl = session_service.get_session_ttl(session_id)
        assert ttl > 0
    
    def test_end_session(self, session_service):
        """Test: Finalizar sesión la elimina"""
        # Arrange
        session_id = session_service.create_session("user-123")
        assert session_service.session_exists(session_id)
        
        # Act
        result = session_service.end_session(session_id)
        
        # Assert
        assert result is True
        assert not session_service.session_exists(session_id)
    
    def test_update_streaming_state(self, session_service):
        """Test: Actualizar estado de streaming"""
        # Arrange
        session_id = session_service.create_session("user-123")
        
        # Act
        result = session_service.update_streaming_state(session_id, True, 3)
        
        # Assert
        assert result is True
        session = session_service.get_session(session_id)
        assert session["is_streaming"] is True
        assert session["current_step"] == 3
    
    def test_pause_streaming(self, session_service):
        """Test: Pausar streaming"""
        # Arrange
        session_id = session_service.create_session("user-123")
        session_service.update_streaming_state(session_id, True, 2)
        
        # Act
        result = session_service.pause_streaming(session_id, 150)
        
        # Assert
        assert result is True
        session = session_service.get_session(session_id)
        assert session["is_paused"] is True
        assert session["pause_position"] == 150
        assert session["is_streaming"] is False
    
    def test_resume_streaming(self, session_service):
        """Test: Reanudar streaming"""
        # Arrange
        session_id = session_service.create_session("user-123")
        session_service.pause_streaming(session_id, 150)
        
        # Act
        session = session_service.resume_streaming(session_id)
        
        # Assert
        assert session["is_paused"] is False
        assert session["is_streaming"] is True
        assert session["pause_position"] == 150  # Preserva la posición
    
    def test_cleanup_expired_sessions(self, session_service):
        """Test: Limpieza retorna número de sesiones activas"""
        # Arrange
        session_service.create_session("user-1")
        session_service.create_session("user-2")
        session_service.create_session("user-3")
        
        # Act
        count = session_service.cleanup_expired_sessions()
        
        # Assert
        assert count == 3


class TestSessionIntegration:
    """Tests de integración de flujos completos"""
    
    def test_full_session_lifecycle(self, session_service):
        """Test: Ciclo de vida completo de una sesión"""
        # 1. Crear sesión
        session_id = session_service.create_session("user-123", "socket-abc")
        assert session_service.session_exists(session_id)
        
        # 2. Iniciar streaming
        session_service.update_streaming_state(session_id, True, 0)
        session = session_service.get_session(session_id)
        assert session["is_streaming"] is True
        
        # 3. Pausar
        session_service.pause_streaming(session_id, 200)
        session = session_service.get_session(session_id)
        assert session["is_paused"] is True
        assert session["pause_position"] == 200
        
        # 4. Reanudar
        session = session_service.resume_streaming(session_id)
        assert session["is_paused"] is False
        assert session["is_streaming"] is True
        
        # 5. Finalizar
        session_service.end_session(session_id)
        assert not session_service.session_exists(session_id)
    
    def test_concurrent_sessions(self, session_service):
        """Test: Múltiples sesiones simultáneas"""
        # Arrange & Act
        session_1 = session_service.create_session("user-1")
        session_2 = session_service.create_session("user-2")
        session_3 = session_service.create_session("user-3")
        
        # Assert
        assert session_service.session_exists(session_1)
        assert session_service.session_exists(session_2)
        assert session_service.session_exists(session_3)
        
        # Modificar una no afecta las otras
        session_service.update_session(session_1, {"test": "value1"})
        session_service.update_session(session_2, {"test": "value2"})
        
        s1 = session_service.get_session(session_1)
        s2 = session_service.get_session(session_2)
        s3 = session_service.get_session(session_3)
        
        assert s1["test"] == "value1"
        assert s2["test"] == "value2"
        assert "test" not in s3
