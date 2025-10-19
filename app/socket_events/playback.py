"""
Eventos de control de reproducción (pause/resume)
"""
from flask_socketio import emit
from app import socketio


@socketio.on("pause_explanation")
def handle_pause(data):
    """
    Pausa la explicación actual
    """
    try:
        current_step = data.get("current_step")
        position = data.get("position_in_step")
        
        # TODO: Implementar lógica de pausa
        
        emit("explanation_paused", {
            "step": current_step,
            "position": position
        })
        
    except Exception as e:
        print(f"Error pausando: {e}")
        emit("error", {
            "code": "PAUSE_ERROR",
            "message": str(e)
        })


@socketio.on("resume_explanation")
def handle_resume(data):
    """
    Reanuda la explicación
    """
    try:
        # TODO: Implementar lógica de reanudación
        
        emit("explanation_resumed", {
            "message": "Continuando explicación"
        })
        
    except Exception as e:
        print(f"Error reanudando: {e}")
        emit("error", {
            "code": "RESUME_ERROR",
            "message": str(e)
        })
