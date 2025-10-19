"""
Repositorio de preguntas del banco
"""
from app.extensions import get_supabase


class QuestionRepository:
    """Acceso a datos de preguntas"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.table = "questions"
    
    def get_all(self, limit: int = 50, offset: int = 0) -> list:
        """
        Obtiene todas las preguntas (paginado)
        
        Args:
            limit: Número de resultados
            offset: Desplazamiento
            
        Returns:
            list: Lista de preguntas
        """
        try:
            response = self.supabase.table(self.table)\
                .select("*")\
                .range(offset, offset + limit - 1)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"Error obteniendo preguntas: {e}")
            return []
    
    def get_by_id(self, question_id: str) -> dict:
        """
        Obtiene una pregunta por ID
        
        Args:
            question_id: UUID de la pregunta
            
        Returns:
            dict: Datos de la pregunta o None
        """
        try:
            response = self.supabase.table(self.table)\
                .select("*")\
                .eq("id", question_id)\
                .single()\
                .execute()
            
            return response.data if response.data else None
            
        except Exception as e:
            print(f"Error obteniendo pregunta: {e}")
            return None
    
    def get_by_subject(self, subject: str, limit: int = 50) -> list:
        """
        Obtiene preguntas por materia
        
        Args:
            subject: Nombre de la materia
            limit: Número de resultados
            
        Returns:
            list: Lista de preguntas
        """
        try:
            response = self.supabase.table(self.table)\
                .select("*")\
                .eq("subject", subject)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"Error obteniendo preguntas por materia: {e}")
            return []
    
    def increment_stats(self, question_id: str, correct: bool = False):
        """
        Incrementa estadísticas de una pregunta
        
        Args:
            question_id: UUID de la pregunta
            correct: Si fue respondida correctamente
        """
        try:
            # Obtener pregunta actual
            question = self.get_by_id(question_id)
            
            if question:
                update_data = {
                    "times_seen": question["times_seen"] + 1
                }
                
                if correct:
                    update_data["times_correct"] = question["times_correct"] + 1
                
                self.supabase.table(self.table)\
                    .update(update_data)\
                    .eq("id", question_id)\
                    .execute()
                    
        except Exception as e:
            print(f"Error actualizando estadísticas: {e}")
