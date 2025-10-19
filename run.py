"""
Punto de entrada principal para la aplicación Flask + SocketIO
"""
from app import create_app, socketio
from app.config import Config

app = create_app()

if __name__ == "__main__":
    socketio.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
        allow_unsafe_werkzeug=True
    )
