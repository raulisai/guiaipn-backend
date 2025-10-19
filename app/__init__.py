"""
App Factory para Flask + SocketIO
"""
from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()


def create_app():
    """
    Crea y configura la aplicación Flask
    """
    app = Flask(__name__)
    
    # Cargar configuración
    from app.config import Config
    app.config.from_object(Config)
    
    # Inicializar extensiones
    from app.extensions import init_extensions
    init_extensions(app, socketio)
    
    # Registrar blueprints (API HTTP)
    from app.api.v1 import auth_routes, question_routes, session_routes
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(question_routes.bp)
    app.register_blueprint(session_routes.bp)
    
    # Inicializar Swagger UI
    from app.api.swagger import init_swagger
    init_swagger(app)
    
    # Registrar event handlers de SocketIO
    from app.socket_events import connection, questions, voice, playback
    
    # Health check
    @app.route("/health")
    def health():
        return {"status": "ok", "service": "guiaipn-backend"}
    
    return app
