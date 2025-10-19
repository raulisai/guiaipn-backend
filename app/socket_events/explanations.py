"""
Socket.IO events para explicaciones de preguntas de examen
"""
from flask_socketio import emit
from app import socketio
from app.services.exam_service import ExamService
from app.services.ai_service import AIService
from app.services.streaming_service import StreamingService
from app.services.session_service import SessionService


@socketio.on('start_explanation')
def handle_start_explanation(data):
    """
    Inicia explicación de una pregunta de examen
    
    Payload:
        - question_id: UUID de la pregunta
        - user_answer: Respuesta del usuario (opcional)
    """
    try:
        question_id = data.get('question_id')
        user_answer = data.get('user_answer')
        
        if not question_id:
            emit('error', {
                'code': 'MISSING_QUESTION_ID',
                'message': 'question_id es requerido'
            })
            return
        
        # Servicios
        exam_service = ExamService()
        ai_service = AIService()
        streaming_service = StreamingService()
        
        # 1. Obtener pregunta
        question = exam_service.question_repo.get_by_id(question_id)
        
        if not question:
            emit('error', {
                'code': 'QUESTION_NOT_FOUND',
                'message': 'Pregunta no encontrada'
            })
            return
        
        # 2. Buscar explicación existente
        explanation = exam_service.get_or_create_explanation(question_id)
        
        # 3. Si no existe, generar con IA
        if not explanation:
            emit('waiting_phrase', {
                'phrase': 'Generando explicación...',
                'category': 'generating',
                'estimated_time': 3000
            })
            
            try:
                # Generar con IA
                ai_response = ai_service.generate_exam_explanation(
                    question,
                    user_answer
                )
                
                # Guardar en DB
                explanation = exam_service.create_explanation(
                    question_id=question_id,
                    explanation_steps=ai_response.get('explanation_steps', []),
                    total_duration=ai_response.get('total_duration', 60),
                    ai_model="gpt-4",
                    prompt_version="v1.0"
                )
                
            except Exception as e:
                print(f"Error generando explicación: {e}")
                emit('error', {
                    'code': 'AI_GENERATION_ERROR',
                    'message': 'Error al generar explicación'
                })
                return
        
        # 4. Iniciar streaming
        emit('explanation_start', {
            'explanation_id': explanation['id'],
            'question_id': question_id,
            'total_steps': len(explanation.get('explanation_steps', [])),
            'estimated_duration': explanation.get('total_duration', 60)
        })
        
        # 5. Stream de pasos
        streaming_service.stream_explanation(
            explanation,
            emit_func=emit
        )
        
        # 6. Completado
        emit('explanation_complete', {
            'explanation_id': explanation['id'],
            'total_duration': explanation.get('total_duration', 60),
            'steps_completed': len(explanation.get('explanation_steps', []))
        })
        
    except Exception as e:
        print(f"Error en start_explanation: {e}")
        emit('error', {
            'code': 'INTERNAL_ERROR',
            'message': 'Error interno del servidor'
        })


@socketio.on('explanation_feedback')
def handle_explanation_feedback(data):
    """
    Registra feedback del usuario sobre una explicación
    
    Payload:
        - explanation_id: UUID de la explicación
        - is_helpful: bool
        - flag_reason: string (opcional)
    """
    try:
        explanation_id = data.get('explanation_id')
        is_helpful = data.get('is_helpful')
        flag_reason = data.get('flag_reason')
        
        if not explanation_id or is_helpful is None:
            emit('error', {
                'code': 'MISSING_FIELDS',
                'message': 'explanation_id e is_helpful son requeridos'
            })
            return
        
        exam_service = ExamService()
        exam_service.record_feedback(
            explanation_id,
            is_helpful,
            flag_reason
        )
        
        emit('feedback_recorded', {
            'explanation_id': explanation_id,
            'success': True
        })
        
    except Exception as e:
        print(f"Error en explanation_feedback: {e}")
        emit('error', {
            'code': 'FEEDBACK_ERROR',
            'message': 'Error al registrar feedback'
        })
