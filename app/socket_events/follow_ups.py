"""
Socket.IO events para preguntas adicionales (follow-up) después de explicaciones
"""
from flask_socketio import emit
from app import socketio
from app.services.exam_service import ExamService
from app.services.ai_service import AIService
from app.services.streaming_service import StreamingService
from app.repositories.ai_answers_repo import AIAnswersRepository
from app.utils.text_processing import normalize_text, generate_hash


@socketio.on('ask_follow_up_question')
def handle_ask_follow_up_question(data):
    """
    Maneja pregunta adicional después de una explicación
    
    Payload:
        - question: Pregunta adicional del usuario
        - related_to: UUID de la pregunta de examen original
    """
    try:
        follow_up_question = data.get('question')
        related_question_id = data.get('related_to')
        
        if not follow_up_question:
            emit('error', {
                'code': 'MISSING_QUESTION',
                'message': 'question es requerido'
            })
            return
        
        if not related_question_id:
            emit('error', {
                'code': 'MISSING_RELATED_ID',
                'message': 'related_to es requerido'
            })
            return
        
        # Servicios
        exam_service = ExamService()
        ai_service = AIService()
        streaming_service = StreamingService()
        ai_answers_repo = AIAnswersRepository()
        
        # 1. Obtener pregunta original
        original_question = exam_service.question_repo.get_by_id(related_question_id)
        
        if not original_question:
            emit('error', {
                'code': 'ORIGINAL_QUESTION_NOT_FOUND',
                'message': 'Pregunta original no encontrada'
            })
            return
        
        # 2. Normalizar y generar hash
        normalized = normalize_text(follow_up_question)
        question_hash = generate_hash(normalized)
        
        # 3. Buscar en cache (ai_answers)
        cached_answer = ai_answers_repo.get_by_hash(question_hash)
        
        # 4. Si no existe, generar con IA
        if not cached_answer:
            emit('waiting_phrase', {
                'phrase': 'Pensando en tu pregunta...',
                'category': 'generating',
                'estimated_time': 3000
            })
            
            try:
                # Obtener explicación previa (opcional)
                previous_explanation = exam_service.explanation_repo.get_by_question_id(
                    related_question_id
                )
                
                # Generar con IA
                ai_response = ai_service.generate_follow_up(
                    follow_up_question,
                    original_question,
                    previous_explanation
                )
                
                # Guardar en DB
                answer_data = {
                    'question_hash': question_hash,
                    'question_text': follow_up_question,
                    'related_question_id': related_question_id,
                    'answer_steps': ai_response.get('answer_steps', []),
                    'total_duration': ai_response.get('total_duration', 90),
                    'generated_by': 'gpt-4'
                }
                
                cached_answer = ai_answers_repo.create(answer_data)
                
            except Exception as e:
                print(f"Error generando follow-up: {e}")
                emit('error', {
                    'code': 'AI_GENERATION_ERROR',
                    'message': 'Error al generar respuesta'
                })
                return
        else:
            # Incrementar uso
            ai_answers_repo.increment_usage(cached_answer['id'])
        
        # 5. Iniciar streaming
        emit('follow_up_start', {
            'answer_id': cached_answer['id'],
            'total_steps': len(cached_answer.get('answer_steps', [])),
            'estimated_duration': cached_answer.get('total_duration', 90),
            'is_follow_up': True
        })
        
        # 6. Stream de pasos
        streaming_service.stream_answer(
            cached_answer,
            emit_func=emit
        )
        
        # 7. Completado
        emit('follow_up_complete', {
            'answer_id': cached_answer['id'],
            'total_duration': cached_answer.get('total_duration', 90),
            'steps_completed': len(cached_answer.get('answer_steps', []))
        })
        
        # 8. Preguntar si tiene más dudas
        emit('follow_up_options', {
            'options': ['more_questions', 'finish']
        })
        
    except Exception as e:
        print(f"Error en ask_follow_up_question: {e}")
        emit('error', {
            'code': 'INTERNAL_ERROR',
            'message': 'Error interno del servidor'
        })
