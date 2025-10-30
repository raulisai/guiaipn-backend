"""Repositorio de respuestas breves de IA."""
from typing import Optional

from app.extensions import get_supabase


class AIBriefAnswersRepository:
    """Acceso a datos para respuestas breves de aclaraciones"""

    def __init__(self):
        self.supabase = get_supabase()
        self.table = "ai_brief_answers"

    def get_by_hash(self, question_hash: str) -> Optional[dict]:
        """Busca una respuesta breve por hash normalizado de aclaración."""
        try:
            response = (
                self.supabase.table(self.table)
                .select("*")
                .eq("question_hash", question_hash)
                .single()
                .execute()
            )
            return response.data if response.data else None
        except Exception as exc:  # pylint: disable=broad-except
            error_str = str(exc)
            if "PGRST116" in error_str or "0 rows" in error_str:
                return None
            print(f"Error buscando respuesta breve: {exc}")
            return None

    def create(self, data: dict) -> Optional[dict]:
        """Inserta una nueva respuesta breve cacheada."""
        try:
            response = self.supabase.table(self.table).insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Error creando respuesta breve: {exc}")
            return None

    def increment_usage(self, record_id: str):
        """Incrementa contador de uso para métricas."""
        try:
            record = (
                self.supabase.table(self.table)
                .select("usage_count")
                .eq("id", record_id)
                .single()
                .execute()
            )
            if record.data is not None:
                usage_count = record.data.get("usage_count", 0) + 1
                (
                    self.supabase.table(self.table)
                    .update({"usage_count": usage_count})
                    .eq("id", record_id)
                    .execute()
                )
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Error incrementando uso de respuesta breve: {exc}")
