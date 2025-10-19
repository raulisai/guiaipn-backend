"""
Eventos de preguntas por Socket.IO
"""
from flask_socketio import emit
from app import socketio
from app.services.question_service import QuestionService
from app.services.streaming_service import StreamingService


@socketio.on("ask_question")
def handle_ask_question(data):
    """
    Maneja una pregunta del usuario
    """
    try:
        question = data.get("question")
        context = data.get("context", {})
        
        if not question:
            emit("error", {
                "code": "INVALID_INPUT",
                "message": "Pregunta vacía"
            })
            return
        
        # Procesar pregunta
        question_service = QuestionService()
        result = question_service.process_question(question, context)
        
        # Iniciar streaming
        streaming_service = StreamingService()
        streaming_service.start_streaming(result)
        
    except Exception as e:
        print(f"Error procesando pregunta: {e}")
        emit("error", {
            "code": "PROCESSING_ERROR",
            "message": str(e)
        })


@socketio.on("interrupt")
def handle_interrupt(data):
    """
    Maneja una interrupción durante la explicación
    """
    try:
        # TODO: Implementar lógica de interrupción
        emit("explanation_paused", {
            "message": "Explicación pausada"
        })
        
    except Exception as e:
        print(f"Error en interrupción: {e}")
        emit("error", {
            "code": "INTERRUPT_ERROR",
            "message": str(e)
        })
