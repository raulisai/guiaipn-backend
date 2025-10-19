"""
Repositorio para explicaciones de preguntas de examen
"""
from typing import Optional
from app.extensions import get_supabase


class ExamExplanationRepository:
    """Acceso a datos de explicaciones de examen"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.table = "exam_question_explanations"
    
    def get_by_question_id(self, question_id: str) -> Optional[dict]:
        """
        Busca explicación por ID de pregunta
        
        Args:
            question_id: UUID de la pregunta
            
        Returns:
            dict: Explicación o None
        """
        try:
            response = self.supabase.table(self.table)\
                .select("*")\
                .eq("question_id", question_id)\
                .single()\
                .execute()
            
            return response.data if response.data else None
            
        except Exception as e:
            print(f"Error buscando explicación: {e}")
            return None
    
    def get_by_id(self, explanation_id: str) -> Optional[dict]:
        """
        Busca explicación por ID
        
        Args:
            explanation_id: UUID de la explicación
            
        Returns:
            dict: Explicación o None
        """
        try:
            response = self.supabase.table(self.table)\
                .select("*")\
                .eq("id", explanation_id)\
                .single()\
                .execute()
            
            return response.data if response.data else None
            
        except Exception as e:
            print(f"Error obteniendo explicación: {e}")
            return None
    
    def create(self, data: dict) -> Optional[dict]:
        """
        Crea una nueva explicación
        
        Args:
            data: Datos de la explicación
            
        Returns:
            dict: Explicación creada
        """
        try:
            response = self.supabase.table(self.table)\
                .insert(data)\
                .execute()
            
            return response.data[0] if response.data else None
            
        except Exception as e:
            print(f"Error creando explicación: {e}")
            return None
    
    def increment_usage(self, explanation_id: str):
        """
        Incrementa contador de uso
        
        Args:
            explanation_id: UUID de la explicación
        """
        try:
            explanation = self.get_by_id(explanation_id)
            
            if explanation:
                self.supabase.table(self.table)\
                    .update({"usage_count": explanation["usage_count"] + 1})\
                    .eq("id", explanation_id)\
                    .execute()
                    
        except Exception as e:
            print(f"Error incrementando uso: {e}")
    
    def record_feedback(self, explanation_id: str, is_helpful: bool, flag_reason: Optional[str] = None):
        """
        Registra feedback de usuario
        
        Args:
            explanation_id: UUID de la explicación
            is_helpful: Si fue marcada como útil
            flag_reason: Razón del flag si existe
        """
        try:
            explanation = self.get_by_id(explanation_id)
            
            if explanation:
                update_data = {
                    "total_votes": explanation["total_votes"] + 1
                }
                
                if is_helpful:
                    update_data["helpful_votes"] = explanation["helpful_votes"] + 1
                else:
                    update_data["unhelpful_votes"] = explanation["unhelpful_votes"] + 1
                
                # Recalcular quality_score
                new_total = update_data["total_votes"]
                new_helpful = update_data.get("helpful_votes", explanation["helpful_votes"])
                update_data["quality_score"] = round(new_helpful / new_total, 2) if new_total > 0 else 0.00
                
                # Si hay flag_reason, marcar como flagged
                if flag_reason:
                    update_data["is_flagged"] = True
                    update_data["flag_reason"] = flag_reason
                
                self.supabase.table(self.table)\
                    .update(update_data)\
                    .eq("id", explanation_id)\
                    .execute()
                    
        except Exception as e:
            print(f"Error registrando feedback: {e}")
    
    def get_flagged(self, limit: int = 50) -> list:
        """
        Obtiene explicaciones marcadas con errores
        
        Args:
            limit: Número de resultados
            
        Returns:
            list: Lista de explicaciones flagged
        """
        try:
            response = self.supabase.table(self.table)\
                .select("*")\
                .eq("is_flagged", True)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"Error obteniendo explicaciones flagged: {e}")
            return []
    
    def get_top_quality(self, limit: int = 50) -> list:
        """
        Obtiene explicaciones con mejor calidad
        
        Args:
            limit: Número de resultados
            
        Returns:
            list: Lista de explicaciones ordenadas por quality_score
        """
        try:
            response = self.supabase.table(self.table)\
                .select("*")\
                .order("quality_score", desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"Error obteniendo top explicaciones: {e}")
            return []
    
    def verify_explanation(self, explanation_id: str, verified_by: str):
        """
        Marca explicación como verificada por humano
        
        Args:
            explanation_id: UUID de la explicación
            verified_by: UUID del usuario que verifica
        """
        try:
            from datetime import datetime
            
            self.supabase.table(self.table)\
                .update({
                    "is_verified": True,
                    "verified_by": verified_by,
                    "verified_at": datetime.utcnow().isoformat()
                })\
                .eq("id", explanation_id)\
                .execute()
                
        except Exception as e:
            print(f"Error verificando explicación: {e}")
