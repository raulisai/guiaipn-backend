"""
Servicio de integración con OpenAI
"""
from openai import OpenAI
from app.config import Config


class AIService:
    """Genera respuestas usando OpenAI"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def generate_answer(self, question: str, context: dict = None) -> dict:
        """
        Genera una respuesta estructurada usando OpenAI
        
        Args:
            question: Pregunta del usuario
            context: Contexto adicional
            
        Returns:
            dict: Respuesta con steps y duración
        """
        prompt = self._build_prompt(question, context)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un tutor experto que explica conceptos paso a paso de forma clara y didáctica."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parsear respuesta
            content = response.choices[0].message.content
            
            # TODO: Parsear JSON estructurado de la respuesta
            # Por ahora retornamos estructura básica
            
            return {
                "steps": [
                    {
                        "step_number": 1,
                        "title": "Explicación",
                        "content": content,
                        "content_type": "text",
                        "has_visual": False
                    }
                ],
                "total_duration": 60
            }
            
        except Exception as e:
            print(f"Error generando respuesta con IA: {e}")
            raise
    
    def _build_prompt(self, question: str, context: dict = None) -> str:
        """
        Construye el prompt para OpenAI
        
        Args:
            question: Pregunta del usuario
            context: Contexto adicional
            
        Returns:
            str: Prompt formateado
        """
        base_prompt = f"""
Explica de forma clara y paso a paso la siguiente pregunta:

{question}

Estructura tu respuesta en pasos numerados, cada uno con:
- Un título descriptivo
- Explicación clara y concisa
- Ejemplos si es necesario

Mantén un tono didáctico y amigable.
"""
        
        if context:
            base_prompt += f"\n\nContexto adicional: {context}"
        
        return base_prompt
