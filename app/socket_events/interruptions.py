"""
Socket.IO events para interrupciones y aclaraciones durante explicaciones
"""
from flask_socketio import emit
from flask import request
from app import socketio
from app.services.ai_service import AIService
from app.services.session_service import SessionService


@socketio.on('interrupt_explanation')
def handle_interrupt_explanation(data):
    """
    Maneja interrupción para aclaración rápida
    
    Payload:
        - clarification_question: Pregunta del usuario
        - current_context: Contexto actual (opcional)
    """
    try:
        clarification_question = data.get('clarification_question')
        current_context = data.get('current_context', {})
        
        if not clarification_question:
            emit('error', {
                'code': 'MISSING_QUESTION',
                'message': 'clarification_question es requerido'
            })
            return
        
        # Servicios
        ai_service = AIService()
        session_service = SessionService()
        
        # Obtener sesión actual
        session_id = request.sid
        session = session_service.get_session(session_id)
        
        if session:
            # Pausar streaming actual
            session_service.pause_streaming(session_id, position=0)
        
        # Emit inicio de aclaración
        emit('clarification_start', {
            'is_brief': True,
            'estimated_duration': 15
        })
        
        try:
            # Generar aclaración con IA
            ai_response = ai_service.generate_clarification(
                clarification_question,
                current_context
            )
            
            # Stream de aclaración (más rápido)
            steps = ai_response.get('clarification_steps', [])
            
            for step in steps:
                emit('clarification_chunk', {
                    'step_number': step.get('step_number'),
                    'title': step.get('title'),
                    'content': step.get('content'),
                    'content_type': step.get('content_type', 'text')
                })
            
            # Completado
            emit('clarification_complete', {
                'total_duration': ai_response.get('total_duration', 15)
            })
            
        except Exception as e:
            print(f"Error generando aclaración: {e}")
            emit('error', {
                'code': 'CLARIFICATION_ERROR',
                'message': 'Error al generar aclaración'
            })
            return
        
        # Preguntar si continuar o nueva pregunta
        emit('clarification_options', {
            'options': ['continue', 'new_question']
        })
        
    except Exception as e:
        print(f"Error en interrupt_explanation: {e}")
        emit('error', {
            'code': 'INTERNAL_ERROR',
            'message': 'Error interno del servidor'
        })


@socketio.on('resume_explanation')
def handle_resume_explanation(data):
    """
    Reanuda la explicación principal después de una interrupción
    """
    try:
        session_id = request.sid
        session_service = SessionService()
        
        # Reanudar streaming
        session_service.resume_streaming(session_id)
        
        emit('explanation_resumed', {
            'success': True
        })
        
    except Exception as e:
        print(f"Error en resume_explanation: {e}")
        emit('error', {
            'code': 'RESUME_ERROR',
            'message': 'Error al reanudar explicación'
        })
