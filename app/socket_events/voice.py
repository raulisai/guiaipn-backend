"""
Eventos de voz por Socket.IO
"""
from flask_socketio import emit
from app import socketio
from app.auth.decorators import require_auth_socket


@socketio.on("voice_start")
@require_auth_socket
def handle_voice_start(data):
    """
    Inicia la grabación de voz
    Requiere autenticación: el token debe estar en data["token"]
    """
    try:
        session_id = data.get("session_id")
        user = data.get("user")  # Inyectado por el decorador
        
        # TODO: Implementar lógica de inicio de grabación
        
        emit("voice_recording_started", {
            "session_id": session_id,
            "max_duration": 60000  # 60 segundos
        })
        
        print(f"✓ Grabación iniciada para usuario: {user.get('email')}")
        
    except Exception as e:
        print(f"Error iniciando grabación: {e}")
        emit("error", {
            "code": "VOICE_START_ERROR",
            "message": str(e)
        })


@socketio.on("voice_complete")
@require_auth_socket
def handle_voice_complete(data):
    """
    Procesa el audio grabado
    Requiere autenticación: el token debe estar en data["token"]
    """
    try:
        audio_data = data.get("audio_data")
        duration = data.get("duration")
        user = data.get("user")  # Inyectado por el decorador
        
        # TODO: Implementar transcripción
        
        emit("voice_transcription_result", {
            "transcription": "Texto transcrito aquí",
            "confidence": 0.95,
            "requires_confirmation": True
        })
        
        print(f"✓ Audio procesado para usuario: {user.get('email')}")
        
    except Exception as e:
        print(f"Error procesando audio: {e}")
        emit("error", {
            "code": "VOICE_PROCESSING_ERROR",
            "message": str(e)
        })
