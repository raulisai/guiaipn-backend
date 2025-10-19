"""
Eventos de preguntas por Socket.IO
"""
from flask_socketio import emit
from app import socketio
from app.auth.decorators import require_auth_socket
from app.services.question_service import QuestionService
from app.services.streaming_service import StreamingService


@socketio.on("ask_question")
@require_auth_socket
def handle_ask_question(data):
    """
    Maneja una pregunta del usuario
    Requiere autenticación: el token debe estar en data["token"]
    """
    try:
        question = data.get("question")
        context = data.get("context", {})
        user = data.get("user")  # Inyectado por el decorador
        
        if not question:
            emit("error", {
                "code": "INVALID_INPUT",
                "message": "Pregunta vacía"
            })
            return
        
        # Procesar pregunta con información del usuario
        question_service = QuestionService()
        result = question_service.process_question(question, context)
        
        # Iniciar streaming
        streaming_service = StreamingService()
        streaming_service.start_streaming(result)
        
        print(f"✓ Pregunta procesada para usuario: {user.get('email')}")
        
    except Exception as e:
        print(f"Error procesando pregunta: {e}")
        emit("error", {
            "code": "PROCESSING_ERROR",
            "message": str(e)
        })


@socketio.on("interrupt")
@require_auth_socket
def handle_interrupt(data):
    """
    Maneja una interrupción durante la explicación
    Requiere autenticación: el token debe estar en data["token"]
    """
    try:
        user = data.get("user")  # Inyectado por el decorador
        
        # TODO: Implementar lógica de interrupción
        emit("explanation_paused", {
            "message": "Explicación pausada"
        })
        
        print(f"✓ Interrupción procesada para usuario: {user.get('email')}")
        
    except Exception as e:
        print(f"Error en interrupción: {e}")
        emit("error", {
            "code": "INTERRUPT_ERROR",
            "message": str(e)
        })
