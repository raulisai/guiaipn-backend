"""
Eventos de voz por Socket.IO
"""
from flask_socketio import emit
from app import socketio


@socketio.on("voice_start")
def handle_voice_start(data):
    """
    Inicia la grabación de voz
    """
    try:
        session_id = data.get("session_id")
        
        # TODO: Implementar lógica de inicio de grabación
        
        emit("voice_recording_started", {
            "session_id": session_id,
            "max_duration": 60000  # 60 segundos
        })
        
    except Exception as e:
        print(f"Error iniciando grabación: {e}")
        emit("error", {
            "code": "VOICE_START_ERROR",
            "message": str(e)
        })


@socketio.on("voice_complete")
def handle_voice_complete(data):
    """
    Procesa el audio grabado
    """
    try:
        audio_data = data.get("audio_data")
        duration = data.get("duration")
        
        # TODO: Implementar transcripción
        
        emit("voice_transcription_result", {
            "transcription": "Texto transcrito aquí",
            "confidence": 0.95,
            "requires_confirmation": True
        })
        
    except Exception as e:
        print(f"Error procesando audio: {e}")
        emit("error", {
            "code": "VOICE_PROCESSING_ERROR",
            "message": str(e)
        })
