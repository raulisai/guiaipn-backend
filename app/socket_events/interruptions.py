"""
Socket.IO events para interrupciones y aclaraciones durante explicaciones
"""
from flask_socketio import emit
from flask import request
from app import socketio
from app.services.ai_service import AIService
from app.services.session_service import SessionService, SessionExpiredError
from app.socket_events.questions import socket_sessions


@socketio.on('interrupt_explanation')
def handle_interrupt_explanation(data):
    """
    Maneja interrupción para aclaración rápida
    
    Payload:
        - clarification_question: Pregunta del usuario
        - current_context: Contexto actual (opcional)
        - response_mode: "brief" (default) o "detailed"
        - session_id: ID de sesión existente (opcional)
    """
    try:
        clarification_question = data.get('clarification_question')
        current_context = data.get('current_context', {})
        response_mode = data.get('response_mode', 'brief')
        provided_session_id = data.get('session_id')

        if not clarification_question:
            emit('error', {
                'code': 'MISSING_QUESTION',
                'message': 'clarification_question es requerido'
            })
            return

        # Servicios
        ai_service = AIService()
        session_service = SessionService()
        socket_id = request.sid

        # Determinar session_id (payload > socket_sessions > None)
        session_id = provided_session_id or socket_sessions.get(socket_id)

        if not session_id:
            emit('error', {
                'code': 'NO_SESSION',
                'message': 'No hay sesión asociada a esta conexión'
            })
            return

        try:
            session = session_service.get_session(session_id)
        except SessionExpiredError:
            emit('error', {
                'code': 'SESSION_EXPIRED',
                'message': 'La sesión ya no está disponible, reinicia la explicación'
            })
            return

        # Re-asociar el session_id al socket actual
        socket_sessions[socket_id] = session_id

        # Actualizar metadata de conexión si cambió
        connection_id = session.get('connection_id')
        if connection_id != socket_id:
            session_service.update_session(session_id, {
                'connection_id': socket_id
            })

        # Pausar streaming actual
        session_service.pause_streaming(session_id, pause_position=session.get('pause_position', 0))

        try:
            ai_response = ai_service.generate_clarification(
                clarification_question,
                current_context,
                response_mode=response_mode
            )
            
            mode = ai_response.get('mode', 'brief')

            if mode == 'detailed':
                steps = ai_response.get('clarification_steps', [])

                if not steps:
                    emit('error', {
                        'code': 'CLARIFICATION_ERROR',
                        'message': 'La respuesta detallada no contiene pasos'
                    })
                    return

                emit('clarification_start', {
                    'mode': 'detailed',
                    'total_steps': len(steps),
                    'estimated_duration': ai_response.get('total_duration', 120)
                })

                for step in steps:
                    emit('clarification_step', {
                        'step_number': step.get('step_number'),
                        'title': step.get('title'),
                        'content': step.get('content'),
                        'content_type': step.get('content_type', 'text'),
                        'canvas_commands': step.get('canvas_commands'),
                        'component_commands': step.get('component_commands')
                    })

                emit('clarification_complete', {
                    'mode': 'detailed',
                    'total_duration': ai_response.get('total_duration', 120)
                })

            else:
                message = ai_response.get('message')
                is_deferred = ai_response.get('is_deferred', False)
                reason = ai_response.get('reason')

                if not message:
                    emit('error', {
                        'code': 'CLARIFICATION_ERROR',
                        'message': 'Respuesta breve inválida'
                    })
                    return

                emit('clarification_message', {
                    'mode': 'brief',
                    'message': message,
                    'is_deferred': is_deferred,
                    'reason': reason
                })
            
        except Exception as e:
            print(f"Error generando aclaración: {e}")
            emit('error', {
                'code': 'CLARIFICATION_ERROR',
                'message': 'Error al generar aclaración'
            })
            return
        
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
