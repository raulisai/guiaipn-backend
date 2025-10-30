"""
Servicio de integración con OpenAI
Genera respuestas estructuradas en formato JSON
"""
import json
import os
from typing import Optional, Dict, List
from openai import OpenAI
from app.config import Config
from app.prompts import (
    get_exam_question_prompt,
    get_clarification_prompt,
    get_follow_up_prompt
)


class AIResponseError(Exception):
    """Excepción cuando la IA no puede generar una respuesta válida"""
    pass


class JSONParseError(Exception):
    """Excepción cuando no se puede parsear el JSON de la respuesta"""
    pass


class AIService:
    """
    Genera respuestas estructuradas usando OpenAI
    
    Formato de respuesta:
    {
        "steps": [
            {
                "title": "Título del paso",
                "type": "text|image|math",
                "content": "Contenido del paso",
                "canvas_commands": []
            }
        ],
        "total_duration": 120
    }
    """
    
    DEFAULT_MODEL = "gpt-4-turbo-preview"  # Soporta response_format json_object
    MAX_TOKENS = 3000
    TEMPERATURE = 0.7
    MAX_RETRY_ATTEMPTS = 2
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el servicio de IA
        
        Args:
            api_key: API key de OpenAI (opcional, usa env si no se provee)
        """
        if api_key is None:
            api_key = os.getenv('OPENAI_API_KEY') or Config.OPENAI_API_KEY
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY no está configurada")
        
        self.client = OpenAI(api_key=api_key)
    
    def build_prompt(self, question: str, context: Optional[Dict] = None) -> Dict[str, str]:
        """
        Construye el prompt system + user para OpenAI
        
        Args:
            question: Pregunta del usuario
            context: Contexto adicional (opcional)
            
        Returns:
            dict: {"system": "...", "user": "..."}
        """
        system_prompt = """Eres un tutor experto del IPN/UNAM que explica conceptos académicos paso a paso.

IMPORTANTE: Debes responder ÚNICAMENTE con un objeto JSON válido, sin texto adicional antes o después.

El JSON debe tener esta estructura EXACTA:
{
    "steps": [
        {
            "title": "Título descriptivo del paso",
            "type": "text",
            "content": "Explicación detallada del paso",
            "canvas_commands": []
        }
    ],
    "total_duration": 120
}

Tipos de paso disponibles:
- "text": Explicación textual
- "math": Fórmulas o ecuaciones matemáticas (usa LaTeX)
- "image": Descripción de diagrama o imagen necesaria

Para canvas_commands, usa comandos como:
- {"type": "draw_axis", "x": 50, "y": 200}
- {"type": "plot_function", "function": "x^2", "color": "#3498db"}
- {"type": "draw_triangle", "points": [[100,100], [200,100], [150,50]]}

Calcula total_duration como: (número de pasos * 30) segundos.

Responde SOLO con el JSON, sin explicaciones adicionales."""

        user_prompt = f"""Pregunta: {question}"""
        
        if context:
            if context.get("subject"):
                user_prompt += f"\nMateria: {context['subject']}"
            if context.get("difficulty"):
                user_prompt += f"\nNivel: {context['difficulty']}"
            if context.get("previous_questions"):
                user_prompt += f"\nPreguntas previas: {context['previous_questions']}"
        
        user_prompt += "\n\nGenera la respuesta en formato JSON como se especificó."
        
        return {
            "system": system_prompt,
            "user": user_prompt
        }
    
    def generate_answer(self, question: str, context: Optional[Dict] = None) -> Dict:
        """
        Genera una respuesta estructurada usando OpenAI
        
        Flujo:
        1. Construye prompt con build_prompt()
        2. Llama a OpenAI ChatCompletions
        3. Parsea JSON de forma segura
        4. Si falla, reintenta hasta 2 veces
        5. Si sigue fallando, lanza excepción
        
        Args:
            question: Pregunta del usuario
            context: Contexto adicional (opcional)
            
        Returns:
            dict: {
                "steps": [...],
                "total_duration": int
            }
            
        Raises:
            AIResponseError: Si OpenAI falla
            JSONParseError: Si no se puede parsear JSON después de reintentos
        """
        prompts = self.build_prompt(question, context)
        
        for attempt in range(self.MAX_RETRY_ATTEMPTS + 1):
            try:
                # Llamar a OpenAI
                response = self._call_openai(prompts["system"], prompts["user"])
                
                # Parsear JSON
                parsed_response = self._parse_json_response(response)
                
                # Validar estructura
                self._validate_response_structure(parsed_response)
                
                return parsed_response
                
            except JSONParseError as e:
                if attempt < self.MAX_RETRY_ATTEMPTS:
                    print(f"⚠ Intento {attempt + 1} falló al parsear JSON: {e}")
                    print(f"🔄 Reintentando... ({attempt + 2}/{self.MAX_RETRY_ATTEMPTS + 1})")
                    continue
                else:
                    print(f"❌ Falló después de {self.MAX_RETRY_ATTEMPTS + 1} intentos")
                    raise JSONParseError(
                        f"No se pudo parsear JSON después de {self.MAX_RETRY_ATTEMPTS + 1} intentos: {e}"
                    )
            
            except AIResponseError as e:
                print(f"❌ Error de OpenAI: {e}")
                raise
        
        # No debería llegar aquí, pero por seguridad
        raise AIResponseError("Error inesperado generando respuesta")
    
    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """
        Llama a la API de OpenAI
        
        Args:
            system_prompt: Prompt del sistema
            user_prompt: Prompt del usuario
            
        Returns:
            str: Respuesta de OpenAI
            
        Raises:
            AIResponseError: Si la llamada falla
        """
        try:
            response = self.client.chat.completions.create(
                model=self.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.TEMPERATURE,
                max_tokens=self.MAX_TOKENS,
                response_format={"type": "json_object"}  # Forzar JSON en GPT-4
            )
            
            content = response.choices[0].message.content
            
            if not content:
                raise AIResponseError("OpenAI retornó respuesta vacía")
            
            return content
            
        except Exception as e:
            raise AIResponseError(f"Error llamando a OpenAI: {str(e)}")
    
    def _parse_json_response(self, response: str) -> Dict:
        """
        Parsea la respuesta JSON de forma segura
        
        Args:
            response: String de respuesta de OpenAI
            
        Returns:
            dict: JSON parseado
            
        Raises:
            JSONParseError: Si no se puede parsear
        """
        try:
            # Intentar parsear directamente
            return json.loads(response)
            
        except json.JSONDecodeError as e:
            # Intentar reparación básica
            try:
                repaired = self._attempt_json_repair(response)
                return json.loads(repaired)
            except:
                raise JSONParseError(f"No se pudo parsear JSON: {e}")
    
    def _attempt_json_repair(self, response: str) -> str:
        """
        Intenta reparar JSON malformado
        
        Args:
            response: String con JSON potencialmente malformado
            
        Returns:
            str: JSON reparado
        """
        # Quitar texto antes del primer {
        if '{' in response:
            response = response[response.index('{'):]
        
        # Quitar texto después del último }
        if '}' in response:
            response = response[:response.rindex('}') + 1]
        
        # Quitar markdown code blocks si existen
        response = response.replace('```json', '').replace('```', '')
        
        return response.strip()
    
    def _validate_response_structure(self, response: Dict) -> None:
        """
        Valida que la respuesta tenga la estructura correcta
        
        Args:
            response: Respuesta parseada
            
        Raises:
            JSONParseError: Si la estructura es inválida
        """
        if not isinstance(response, dict):
            raise JSONParseError("La respuesta no es un objeto JSON")
        
        if "steps" not in response:
            raise JSONParseError("La respuesta no tiene campo 'steps'")
        
        if not isinstance(response["steps"], list):
            raise JSONParseError("'steps' debe ser un array")
        
        if len(response["steps"]) == 0:
            raise JSONParseError("'steps' no puede estar vacío")
        
        # Validar cada step
        for i, step in enumerate(response["steps"]):
            if not isinstance(step, dict):
                raise JSONParseError(f"Step {i} no es un objeto")
            
            required_fields = ["title", "type", "content"]
            for field in required_fields:
                if field not in step:
                    raise JSONParseError(f"Step {i} no tiene campo '{field}'")
            
            valid_types = ["text", "image", "math"]
            if step["type"] not in valid_types:
                raise JSONParseError(
                    f"Step {i} tiene type inválido: {step['type']}. "
                    f"Debe ser uno de: {valid_types}"
                )
        
        if "total_duration" not in response:
            raise JSONParseError("La respuesta no tiene campo 'total_duration'")
        
        if not isinstance(response["total_duration"], (int, float)):
            raise JSONParseError("'total_duration' debe ser un número")
    
    def generate_exam_explanation(
        self,
        question: dict,
        user_answer: str = None,
        model: str = None
    ) -> Dict:
        """
        Genera explicación para pregunta de examen usando prompt modular
        
        Args:
            question: Diccionario con datos de la pregunta
            user_answer: Respuesta del usuario (opcional)
            model: Modelo de OpenAI a usar (opcional)
            
        Returns:
            dict: {
                "explanation_steps": [...],
                "total_duration": int
            }
        """
        prompt = get_exam_question_prompt(question, user_answer)
        model = model or self.DEFAULT_MODEL
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.MAX_TOKENS,
                temperature=self.TEMPERATURE,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            return parsed
            
        except Exception as e:
            print(f"Error generando explicación de examen: {e}")
            raise AIResponseError(f"Error al generar explicación: {str(e)}")
    
    def generate_clarification(
        self,
        clarification_question: str,
        current_context: dict,
        response_mode: str = "brief",
        model: str = None
    ) -> Dict:
        """
        Genera respuesta para interrupción/aclaración
        
        Args:
            clarification_question: Pregunta del usuario
            current_context: Contexto actual de la explicación
            response_mode: "brief" para mensaje corto o "detailed" para pasos estructurados
            model: Modelo de OpenAI a usar (opcional)
            
        Returns:
            dict: dependiendo del modo solicitado
                - brief: {"mode": "brief", "message": str, "is_deferred": bool, "reason": Optional[str]}
                - detailed: {"mode": "detailed", "clarification_steps": [...], "total_duration": int}
        """
        prompt = get_clarification_prompt(
            clarification_question,
            current_context,
            response_mode=response_mode
        )
        model = model or self.DEFAULT_MODEL
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,  # Más corto para aclaraciones
                temperature=self.TEMPERATURE,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            return parsed
            
        except Exception as e:
            print(f"Error generando aclaración: {e}")
            raise AIResponseError(f"Error al generar aclaración: {str(e)}")
    
    def generate_follow_up(
        self,
        follow_up_question: str,
        original_question: dict,
        previous_explanation: dict = None,
        model: str = None
    ) -> Dict:
        """
        Genera respuesta completa para pregunta adicional (follow-up)
        
        Args:
            follow_up_question: Pregunta adicional del usuario
            original_question: Pregunta de examen original
            previous_explanation: Explicación previa (opcional)
            model: Modelo de OpenAI a usar (opcional)
            
        Returns:
            dict: {
                "answer_steps": [...],
                "total_duration": int
            }
        """
        prompt = get_follow_up_prompt(
            follow_up_question,
            original_question,
            previous_explanation
        )
        model = model or self.DEFAULT_MODEL
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.MAX_TOKENS,
                temperature=self.TEMPERATURE,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            return parsed
            
        except Exception as e:
            print(f"Error generando follow-up: {e}")
            raise AIResponseError(f"Error al generar follow-up: {str(e)}")
