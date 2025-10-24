"""
Servicio de streaming de respuestas en tiempo real
Maneja el envío progresivo de respuestas al cliente via Socket.IO
"""
import time
from typing import Optional, Dict, List
from flask_socketio import emit
from app.services.session_service import SessionService


class StreamingService:
    """
    Gestiona el streaming de respuestas al cliente
    
    Características:
    - Streaming progresivo de contenido (efecto typewriter)
    - Soporte para pause/resume
    - Manejo de canvas commands
    - Integración con Redis sessions
    - Tipos de contenido: text, math, image
    """
    
    CHUNK_SIZE = 50  # Caracteres por chunk
    CHUNK_DELAY = 0.05  # Segundos entre chunks
    
    def __init__(self, session_service: Optional[SessionService] = None):
        """
        Inicializa el servicio de streaming
        
        Args:
            session_service: Servicio de sesiones (opcional)
        """
        if session_service is None:
            session_service = SessionService()
        
        self.session_service = session_service
    
    def start_streaming(self, answer_data: Dict, session_id: str) -> None:
        """
        Inicia el streaming de una respuesta
        
        Args:
            answer_data: Datos de la respuesta con steps
            session_id: ID de la sesión
            
        Emite:
            - explanation_start: Metadata inicial
            - step_start: Inicio de cada paso
            - content_chunk: Chunks de contenido
            - canvas_command: Comandos de visualización
            - step_complete: Fin de cada paso
            - explanation_complete: Fin de la explicación
        """
        try:
            steps = answer_data.get("steps", [])
            total_duration = answer_data.get("total_duration", 60)
            
            # Actualizar sesión: iniciar streaming
            self.session_service.update_streaming_state(
                session_id=session_id,
                is_streaming=True,
                current_step=0
            )
            
            # Enviar metadata inicial
            emit("explanation_start", {
                "total_steps": len(steps),
                "estimated_duration": total_duration,
                "question_hash": answer_data.get("question_hash")
            })
            
            # Streaming de cada paso
            for step_index, step in enumerate(steps):
                # Verificar si está pausado
                session = self.session_service.get_session(session_id)
                if session and session.get("is_paused"):
                    emit("streaming_paused", {
                        "step": step_index,
                        "message": "Streaming pausado por el usuario"
                    })
                    break
                
                # Actualizar paso actual
                self.session_service.update_streaming_state(
                    session_id=session_id,
                    is_streaming=True,
                    current_step=step_index
                )
                
                # Stream del paso
                self._stream_step(step, step_index, session_id)
            
            # Finalizar
            self.session_service.update_streaming_state(
                session_id=session_id,
                is_streaming=False,
                current_step=len(steps)
            )
            
            emit("explanation_complete", {
                "total_duration": total_duration,
                "steps_completed": len(steps)
            })
            
        except Exception as e:
            print(f"❌ Error en streaming: {e}")
            emit("error", {
                "code": "STREAMING_ERROR",
                "message": str(e)
            })
    
    def _stream_step(self, step: Dict, step_index: int, session_id: str) -> None:
        """
        Hace streaming de un paso individual
        
        Args:
            step: Datos del paso
            step_index: Índice del paso (0-based)
            session_id: ID de la sesión
        """
        title = step.get("title", "")
        content = step.get("content", "")
        step_type = step.get("type", "text")
        canvas_commands = step.get("canvas_commands", [])
        component_commands = step.get("component_commands", [])
        
        # Enviar inicio del paso
        emit("step_start", {
            "step": step_index,
            "title": title,
            "type": step_type
        })
        
        # Enviar canvas commands si existen
        if canvas_commands:
            for command in canvas_commands:
                emit("canvas_command", {
                    "step": step_index,
                    "command": command
                })
                time.sleep(0.1)
        
        # Enviar component commands si existen
        if component_commands:
            for command in component_commands:
                emit("component_command", {
                    "step": step_index,
                    "command": command
                })
                time.sleep(0.1)
        
        # Streaming de contenido en chunks
        self._stream_content(content, step_index, session_id)
        
        # Finalizar paso
        emit("step_complete", {
            "step": step_index
        })
    
    def _stream_content(self, content: str, step_index: int, session_id: str) -> None:
        """
        Hace streaming del contenido en chunks
        
        Args:
            content: Contenido a enviar
            step_index: Índice del paso
            session_id: ID de la sesión
        """
        total_length = len(content)
        position = 0
        
        while position < total_length:
            # Verificar si está pausado
            session = self.session_service.get_session(session_id)
            if session and session.get("is_paused"):
                # Guardar posición de pausa
                self.session_service.pause_streaming(session_id, position)
                break
            
            # Calcular chunk
            chunk_end = min(position + self.CHUNK_SIZE, total_length)
            chunk = content[position:chunk_end]
            
            # Enviar chunk
            emit("content_chunk", {
                "step": step_index,
                "chunk": chunk,
                "position": position,
                "is_final": chunk_end >= total_length
            })
            
            position = chunk_end
            
            # Delay para efecto typewriter
            if position < total_length:
                time.sleep(self.CHUNK_DELAY)
    
    def resume_streaming(self, session_id: str, answer_data: Dict) -> None:
        """
        Reanuda el streaming desde donde se pausó
        
        Args:
            session_id: ID de la sesión
            answer_data: Datos de la respuesta
        """
        try:
            session = self.session_service.get_session(session_id)
            
            if not session:
                emit("error", {
                    "code": "SESSION_NOT_FOUND",
                    "message": "Sesión no encontrada"
                })
                return
            
            if not session.get("is_paused"):
                emit("error", {
                    "code": "NOT_PAUSED",
                    "message": "El streaming no está pausado"
                })
                return
            
            # Obtener posición de pausa
            pause_position = session.get("pause_position", 0)
            current_step = session.get("current_step", 0)
            
            # Reanudar sesión
            self.session_service.resume_streaming(session_id)
            
            emit("streaming_resumed", {
                "step": current_step,
                "position": pause_position
            })
            
            # Continuar streaming desde el paso actual
            steps = answer_data.get("steps", [])
            
            if current_step < len(steps):
                step = steps[current_step]
                content = step.get("content", "")
                
                # Continuar desde la posición de pausa
                remaining_content = content[pause_position:]
                self._stream_content(remaining_content, current_step, session_id)
                
                emit("step_complete", {"step": current_step})
                
                # Continuar con los pasos restantes
                for step_index in range(current_step + 1, len(steps)):
                    session = self.session_service.get_session(session_id)
                    if session and session.get("is_paused"):
                        break
                    
                    self._stream_step(steps[step_index], step_index, session_id)
                
                # Finalizar si completó todos los pasos
                session = self.session_service.get_session(session_id)
                if session and not session.get("is_paused"):
                    emit("explanation_complete", {
                        "total_duration": answer_data.get("total_duration", 60),
                        "steps_completed": len(steps)
                    })
            
        except Exception as e:
            print(f"❌ Error reanudando streaming: {e}")
            emit("error", {
                "code": "RESUME_ERROR",
                "message": str(e)
            })
    
    def stream_explanation(self, explanation: Dict, emit_func=None) -> None:
        """
        Stream de explicación de examen (sin sesión Redis)
        
        Args:
            explanation: Datos de la explicación con explanation_steps
            emit_func: Función emit de Socket.IO (opcional)
        """
        if emit_func is None:
            emit_func = emit
        
        try:
            steps = explanation.get('explanation_steps', [])
            
            for step in steps:
                step_number = step.get('step_number', 0)
                
                # Emit inicio de paso
                emit_func('step_start', {
                    'step_number': step_number,
                    'title': step.get('title', ''),
                    'content_type': step.get('content_type', 'text'),
                    'has_visual': step.get('has_visual', False)
                })
                
                # Stream de contenido
                content = step.get('content', '')
                self._stream_content_simple(content, step_number, emit_func)
                
                # Canvas commands si existen
                if step.get('has_visual') and step.get('canvas_commands'):
                    for command in step['canvas_commands']:
                        emit_func('canvas_command', {
                            'step_number': step_number,
                            'command': command
                        })
                        time.sleep(0.1)
                
                # Component commands si existen
                if step.get('has_visual') and step.get('component_commands'):
                    for command in step['component_commands']:
                        emit_func('component_command', {
                            'step_number': step_number,
                            'command': command
                        })
                        time.sleep(0.1)
                
                # Emit fin de paso
                emit_func('step_complete', {
                    'step_number': step_number
                })
                
        except Exception as e:
            print(f"Error en stream_explanation: {e}")
            emit_func('error', {
                'code': 'STREAMING_ERROR',
                'message': str(e)
            })
    
    def stream_answer(self, answer: Dict, emit_func=None) -> None:
        """
        Stream de respuesta (ai_answers) para follow-ups
        
        Args:
            answer: Datos de la respuesta con answer_steps
            emit_func: Función emit de Socket.IO (opcional)
        """
        if emit_func is None:
            emit_func = emit
        
        try:
            steps = answer.get('answer_steps', [])
            
            for step in steps:
                step_number = step.get('step_number', 0)
                
                # Emit inicio de paso
                emit_func('step_start', {
                    'step_number': step_number,
                    'title': step.get('title', ''),
                    'content_type': step.get('content_type', 'text'),
                    'has_visual': step.get('has_visual', False)
                })
                
                # Stream de contenido
                content = step.get('content', '')
                self._stream_content_simple(content, step_number, emit_func)
                
                # Canvas commands si existen
                if step.get('has_visual') and step.get('canvas_commands'):
                    for command in step['canvas_commands']:
                        emit_func('canvas_command', {
                            'step_number': step_number,
                            'command': command
                        })
                        time.sleep(0.1)
                
                # Component commands si existen
                if step.get('has_visual') and step.get('component_commands'):
                    for command in step['component_commands']:
                        emit_func('component_command', {
                            'step_number': step_number,
                            'command': command
                        })
                        time.sleep(0.1)
                
                # Emit fin de paso
                emit_func('step_complete', {
                    'step_number': step_number
                })
                
        except Exception as e:
            print(f"Error en stream_answer: {e}")
            emit_func('error', {
                'code': 'STREAMING_ERROR',
                'message': str(e)
            })
    
    def _stream_content_simple(self, content: str, step_number: int, emit_func) -> None:
        """
        Stream simple de contenido sin manejo de sesión
        
        Args:
            content: Contenido a enviar
            step_number: Número del paso
            emit_func: Función emit
        """
        chunks = [content[i:i + self.CHUNK_SIZE] for i in range(0, len(content), self.CHUNK_SIZE)]
        
        for i, chunk in enumerate(chunks):
            emit_func('content_chunk', {
                'step_number': step_number,
                'chunk': chunk,
                'position': i * self.CHUNK_SIZE,
                'is_final': i == len(chunks) - 1
            })
            time.sleep(self.CHUNK_DELAY)
