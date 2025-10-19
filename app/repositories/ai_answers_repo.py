"""
Repositorio de respuestas IA
"""
from app.extensions import get_supabase


class AIAnswersRepository:
    """Acceso a datos de respuestas IA"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.table = "ai_answers"
    
    def get_by_hash(self, question_hash: str) -> dict:
        """
        Busca una respuesta por hash de pregunta
        
        Args:
            question_hash: SHA256 de la pregunta normalizada
            
        Returns:
            dict: Respuesta o None
        """
        try:
            response = self.supabase.table(self.table)\
                .select("*")\
                .eq("question_hash", question_hash)\
                .single()\
                .execute()
            
            return response.data if response.data else None
            
        except Exception as e:
            print(f"Error buscando respuesta: {e}")
            return None
    
    def create(self, data: dict) -> dict:
        """
        Crea una nueva respuesta IA
        
        Args:
            data: Datos de la respuesta
            
        Returns:
            dict: Respuesta creada
        """
        try:
            response = self.supabase.table(self.table)\
                .insert(data)\
                .execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            print(f"Error creando respuesta: {e}")
            return None
    
    def increment_usage(self, answer_id: str):
        """
        Incrementa el contador de uso de una respuesta
        
        Args:
            answer_id: UUID de la respuesta
        """
        try:
            # Usar RPC de Supabase para incrementar atómicamente
            self.supabase.rpc(
                "increment_answer_usage",
                {"answer_id": answer_id}
            ).execute()
            
        except Exception as e:
            # Si la función RPC no existe, hacerlo manualmente
            try:
                answer = self.supabase.table(self.table)\
                    .select("usage_count")\
                    .eq("id", answer_id)\
                    .single()\
                    .execute()
                
                if answer.data:
                    self.supabase.table(self.table)\
                        .update({"usage_count": answer.data["usage_count"] + 1})\
                        .eq("id", answer_id)\
                        .execute()
                        
            except Exception as inner_e:
                print(f"Error incrementando uso: {inner_e}")
    
    def update_votes(self, answer_id: str, helpful: bool):
        """
        Actualiza votos de una respuesta
        
        Args:
            answer_id: UUID de la respuesta
            helpful: Si fue marcada como útil
        """
        try:
            answer = self.supabase.table(self.table)\
                .select("helpful_votes", "total_votes")\
                .eq("id", answer_id)\
                .single()\
                .execute()
            
            if answer.data:
                update_data = {
                    "total_votes": answer.data["total_votes"] + 1
                }
                
                if helpful:
                    update_data["helpful_votes"] = answer.data["helpful_votes"] + 1
                
                self.supabase.table(self.table)\
                    .update(update_data)\
                    .eq("id", answer_id)\
                    .execute()
                    
        except Exception as e:
            print(f"Error actualizando votos: {e}")
