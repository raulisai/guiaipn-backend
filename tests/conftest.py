"""
Configuración de pytest
"""
import pytest
from app import create_app


@pytest.fixture
def app():
    """Fixture de la aplicación Flask"""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Fixture del cliente de pruebas"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Fixture del CLI runner"""
    return app.test_cli_runner()
