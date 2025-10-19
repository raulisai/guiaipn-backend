"""
Eventos de preguntas por Socket.IO
Maneja el flujo completo de ask_question con streaming
"""
from flask import request
from flask_socketio import emit
from app import socketio
from app.auth.decorators import require_auth_socket
from app.services.question_service import QuestionService, QuestionValidationError
from app.services.streaming_service import StreamingService
from app.services.ai_service import AIService, AIResponseError, JSONParseError
from app.services.session_service import SessionService
from app.repositories.ai_answers_repo import AIAnswersRepository

# Mapeo de socket_id -> session_id
socket_sessions = {}

# Frases de espera mientras se genera la respuesta
WAITING_PHRASES = [
    "Analizando tu pregunta...",
    "Consultando la base de conocimiento...",
    "Preparando una explicación detallada...",
    "Organizando los pasos de la solución..."
]


@socketio.on("ask_question")
@require_auth_socket
def handle_ask_question(data):
    """
    Maneja una pregunta del usuario
    
    Flujo:
    1. Verificar rate limit (TODO)
    2. Validar y procesar pregunta con QuestionService
    3. Si existe en cache: streaming directo
    4. Si no existe: emitir waiting_phrase, generar con IA, guardar, streaming
    
    Requiere autenticación: el token debe estar en data["token"]
    
    Payload:
        {
            "token": "jwt_token",
            "question": "¿Qué es la energía cinética?",
            "context": {
                "subject": "física",
                "difficulty": "medium"
            }
        }
    """
    try:
        question_text = data.get("question")
        context = data.get("context", {})
        user = data.get("user")  # Inyectado por el decorador
        user_id = user.get("id")
        
        if not question_text:
            emit("error", {
                "code": "INVALID_INPUT",
                "message": "Pregunta vacía"
            })
            return
        
        # Obtener o crear sesión
        socket_id = request.sid
        session_service = SessionService()
        
        if socket_id not in socket_sessions:
            # Crear nueva sesión
            session_id = session_service.create_session(
                user_id=user_id,
                connection_id=socket_id
            )
            socket_sessions[socket_id] = session_id
        else:
            session_id = socket_sessions[socket_id]
        
        # TODO: Verificar rate limit aquí
        # rate_limiter.check_limit(user_id)
        
        # Procesar pregunta
        question_service = QuestionService()
        
        try:
            result = question_service.process_question(user_id, question_text)
        except QuestionValidationError as e:
            emit("error", {
                "code": "VALIDATION_ERROR",
                "message": str(e)
            })
            return
        
        # Actualizar sesión con hash de pregunta
        session_service.update_session(session_id, {
            "current_question": result["question_hash"]
        })
        
        # Iniciar streaming service
        streaming_service = StreamingService(session_service)
        
        if result["cached"]:
            # Respuesta en cache - streaming directo
            print(f"✓ Respuesta en cache para: {question_text[:50]}...")
            
            answer_data = {
                "steps": result["answer_steps"],
                "total_duration": result["total_duration"],
                "question_hash": result["question_hash"]
            }
            
            streaming_service.start_streaming(answer_data, session_id)
            
        else:
            # No existe en cache - generar con IA
            print(f"🤖 Generando respuesta con IA para: {question_text[:50]}...")
            
            # Emitir frase de espera
            import random
            waiting_phrase = random.choice(WAITING_PHRASES)
            emit("waiting_phrase", {
                "message": waiting_phrase
            })
            
            # Generar con IA
            ai_service = AIService()
            
            try:
                ai_response = ai_service.generate_answer(question_text, context)
            except (AIResponseError, JSONParseError) as e:
                emit("error", {
                    "code": "AI_GENERATION_ERROR",
                    "message": f"Error generando respuesta: {str(e)}"
                })
                return
            
            # Guardar en DB
            ai_answers_repo = AIAnswersRepository()
            
            try:
                saved_answer = ai_answers_repo.create({
                    "question_hash": result["question_hash"],
                    "question_text": question_text,
                    "answer_steps": ai_response["steps"],
                    "total_duration": ai_response["total_duration"],
                    "generated_by": "gpt-4"
                })
                
                print(f"✓ Respuesta guardada en DB: {saved_answer['id']}")
                
            except Exception as e:
                print(f"⚠ Error guardando en DB: {e}")
                # Continuar con streaming aunque falle el guardado
            
            # Iniciar streaming
            answer_data = {
                "steps": ai_response["steps"],
                "total_duration": ai_response["total_duration"],
                "question_hash": result["question_hash"]
            }
            
            streaming_service.start_streaming(answer_data, session_id)
        
        print(f"✓ Pregunta procesada para usuario: {user.get('email')}")
        
    except Exception as e:
        print(f"❌ Error procesando pregunta: {e}")
        import traceback
        traceback.print_exc()
        
        emit("error", {
            "code": "PROCESSING_ERROR",
            "message": str(e)
        })


@socketio.on("pause_explanation")
@require_auth_socket
def handle_pause_explanation(data):
    """
    Pausa el streaming de la explicación actual
    
    Payload:
        {
            "token": "jwt_token"
        }
    """
    try:
        socket_id = request.sid
        
        if socket_id not in socket_sessions:
            emit("error", {
                "code": "NO_SESSION",
                "message": "No hay sesión activa"
            })
            return
        
        session_id = socket_sessions[socket_id]
        session_service = SessionService()
        
        # Pausar en Redis
        session_service.pause_streaming(session_id, position=0)
        
        emit("explanation_paused", {
            "message": "Explicación pausada",
            "session_id": session_id
        })
        
        print(f"⏸ Streaming pausado para sesión: {session_id}")
        
    except Exception as e:
        print(f"❌ Error pausando explicación: {e}")
        emit("error", {
            "code": "PAUSE_ERROR",
            "message": str(e)
        })


@socketio.on("resume_explanation")
@require_auth_socket
def handle_resume_explanation(data):
    """
    Reanuda el streaming de la explicación pausada
    
    Payload:
        {
            "token": "jwt_token",
            "answer_data": {...}  # Datos de la respuesta (opcional si está en sesión)
        }
    """
    try:
        socket_id = request.sid
        
        if socket_id not in socket_sessions:
            emit("error", {
                "code": "NO_SESSION",
                "message": "No hay sesión activa"
            })
            return
        
        session_id = socket_sessions[socket_id]
        session_service = SessionService()
        streaming_service = StreamingService(session_service)
        
        # Obtener answer_data del payload o de la sesión
        answer_data = data.get("answer_data")
        
        if not answer_data:
            # Intentar recuperar de la sesión o DB
            session = session_service.get_session(session_id)
            question_hash = session.get("current_question")
            
            if question_hash:
                ai_answers_repo = AIAnswersRepository()
                cached_answer = ai_answers_repo.get_by_hash(question_hash)
                
                if cached_answer:
                    answer_data = {
                        "steps": cached_answer["answer_steps"],
                        "total_duration": cached_answer["total_duration"],
                        "question_hash": question_hash
                    }
        
        if not answer_data:
            emit("error", {
                "code": "NO_ANSWER_DATA",
                "message": "No se encontraron datos de la respuesta"
            })
            return
        
        # Reanudar streaming
        streaming_service.resume_streaming(session_id, answer_data)
        
        print(f"▶ Streaming reanudado para sesión: {session_id}")
        
    except Exception as e:
        print(f"❌ Error reanudando explicación: {e}")
        emit("error", {
            "code": "RESUME_ERROR",
            "message": str(e)
        })
