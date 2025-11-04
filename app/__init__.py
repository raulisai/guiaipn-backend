"""App Factory para Flask + SocketIO"""
import logging
import time
from typing import Any

from flask import Flask, g, request
from flask_socketio import SocketIO

socketio = SocketIO()


def _configure_logging(app: Flask, debug_enabled: bool) -> logging.Logger:
    """Configura el logger principal de la aplicación."""
    logger = app.logger
    level = logging.DEBUG if debug_enabled else logging.INFO
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.debug("Logger configurado con nivel %s", logging.getLevelName(level))
    return logger


def _sanitize_headers(headers: dict[str, Any]) -> dict[str, Any]:
    """Oculta encabezados sensibles como Authorization."""
    return {
        key: ("***" if key.lower() == "authorization" else value)
        for key, value in headers.items()
    }


def create_app():
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__)

    # Cargar configuración
    from app.config import Config

    app.config.from_object(Config)
    logger = _configure_logging(app, Config.DEBUG)

    # Inicializar extensiones
    from app.extensions import init_extensions

    init_extensions(app, socketio)

    # Registrar blueprints (API HTTP)
    from app.api.v1 import auth_routes, question_routes, session_routes, payment_routes

    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(question_routes.bp)
    app.register_blueprint(session_routes.bp)
    app.register_blueprint(payment_routes.bp)

    # Inicializar Swagger UI
    from app.api.swagger import init_swagger

    init_swagger(app)

    # Registrar event handlers de SocketIO
    from app.socket_events import connection, questions, voice, playback

    @app.before_request
    def log_request() -> None:
        g.request_start = time.perf_counter()
        full_path = request.full_path.rstrip("?")
        logger.info("➡️  %s %s (from %s)", request.method, full_path, request.remote_addr)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Headers: %s", _sanitize_headers(dict(request.headers)))
            if request.method in {"POST", "PUT", "PATCH"}:
                body = request.get_json(silent=True)
                if body is not None:
                    logger.debug("Body: %s", body)

    @app.after_request
    def log_response(response):
        start_time = getattr(g, "request_start", None)
        duration_ms = None
        if start_time is not None:
            duration_ms = (time.perf_counter() - start_time) * 1000
        full_path = request.full_path.rstrip("?")
        message = "⬅️  %s %s -> %s" % (request.method, full_path, response.status_code)
        if duration_ms is not None:
            message += f" ({duration_ms:.2f} ms)"
        logger.info(message)

        if logger.isEnabledFor(logging.DEBUG) and response.is_json:
            try:
                logger.debug("Response JSON: %s", response.get_json())
            except Exception:  # pragma: no cover - fallback
                pass
        return response

    # Health check
    @app.route("/health")
    def health():
        return {"status": "ok", "service": "guiaipn-backend"}

    return app
