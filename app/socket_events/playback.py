"""
Eventos de control de reproducción (pause/resume)
"""
from flask_socketio import emit
from app import socketio
from app.auth.decorators import require_auth_socket


@socketio.on("pause_explanation")
@require_auth_socket
def handle_pause(data):
    """
    Pausa la explicación actual
    Requiere autenticación: el token debe estar en data["token"]
    """
    try:
        current_step = data.get("current_step")
        position = data.get("position_in_step")
        user = data.get("user")  # Inyectado por el decorador
        
        # TODO: Implementar lógica de pausa
        
        emit("explanation_paused", {
            "step": current_step,
            "position": position
        })
        
        print(f"✓ Explicación pausada para usuario: {user.get('email')}")
        
    except Exception as e:
        print(f"Error pausando: {e}")
        emit("error", {
            "code": "PAUSE_ERROR",
            "message": str(e)
        })


@socketio.on("resume_explanation")
@require_auth_socket
def handle_resume(data):
    """
    Reanuda la explicación
    Requiere autenticación: el token debe estar en data["token"]
    """
    try:
        user = data.get("user")  # Inyectado por el decorador
        
        # TODO: Implementar lógica de reanudación
        
        emit("explanation_resumed", {
            "message": "Continuando explicación"
        })
        
        print(f"✓ Explicación reanudada para usuario: {user.get('email')}")
        
    except Exception as e:
        print(f"Error reanudando: {e}")
        emit("error", {
            "code": "RESUME_ERROR",
            "message": str(e)
        })
