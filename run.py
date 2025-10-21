"""
Punto de entrada principal para la aplicación Flask + SocketIO
"""
from app import create_app, socketio
from app.config import Config

app = create_app()

if __name__ == "__main__":
    # Flask-SocketIO will handle gevent monkey patching automatically
    # when async_mode="gevent" is set in extensions.py
    socketio.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
        allow_unsafe_werkzeug=True
    )
