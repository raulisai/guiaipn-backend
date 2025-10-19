"""
Servicio de streaming de respuestas
"""
import time
from flask_socketio import emit


class StreamingService:
    """Gestiona el streaming de respuestas al cliente"""
    
    def start_streaming(self, answer_data: dict):
        """
        Inicia el streaming de una respuesta
        
        Args:
            answer_data: Datos de la respuesta con steps
        """
        try:
            steps = answer_data["answer_steps"]
            total_duration = answer_data["total_duration"]
            
            # Enviar metadata inicial
            emit("explanation_start", {
                "total_steps": len(steps),
                "estimated_duration": total_duration,
                "question_hash": answer_data["question_hash"]
            })
            
            # Streaming de cada paso
            for step in steps:
                self._stream_step(step)
            
            # Finalizar
            emit("explanation_complete", {
                "total_duration": total_duration,
                "steps_completed": len(steps)
            })
            
        except Exception as e:
            print(f"Error en streaming: {e}")
            emit("error", {
                "code": "STREAMING_ERROR",
                "message": str(e)
            })
    
    def _stream_step(self, step: dict):
        """
        Hace streaming de un paso individual
        
        Args:
            step: Datos del paso
        """
        step_number = step.get("step_number", 1)
        title = step.get("title", "")
        content = step.get("content", "")
        
        # Enviar inicio del paso
        emit("step_start", {
            "step_number": step_number,
            "title": title,
            "content_type": step.get("content_type", "text"),
            "has_visual": step.get("has_visual", False)
        })
        
        # Streaming de contenido en chunks
        chunk_size = 50
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i + chunk_size]
            
            emit("content_chunk", {
                "step_number": step_number,
                "chunk": chunk,
                "position": i,
                "is_final": i + chunk_size >= len(content)
            })
            
            # Simular delay para efecto typewriter
            time.sleep(0.05)
        
        # Finalizar paso
        emit("step_complete", {
            "step_number": step_number,
            "duration_actual": 15000  # TODO: calcular duración real
        })
