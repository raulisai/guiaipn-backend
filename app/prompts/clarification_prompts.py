"""
Prompts para aclaraciones rápidas durante explicaciones
"""


def get_clarification_prompt(
    clarification_question: str,
    current_context: dict,
    response_mode: str = "brief"
) -> str:
    """
    Genera prompt para responder una interrupción/aclaración según el modo solicitado
    
    Args:
        clarification_question: Pregunta del usuario
        current_context: Contexto actual (pregunta original, paso actual, etc)
        response_mode: "brief" para respuesta corta o "detailed" para explicación en pasos
        
    Returns:
        str: Prompt completo para la IA
    """
    
    normalized_mode = (response_mode or "brief").strip().lower()
    if normalized_mode not in {"brief", "detailed"}:
        normalized_mode = "brief"
    
    if normalized_mode == "brief":
        system_prompt = """Eres un profesor paciente que responde dudas rápidas durante una explicación.

MODO ACTUAL: BRIEF (respuesta corta)

INSTRUCCIONES:
- Responde en una sola oración o dos como máximo.
- No enumeres pasos ni generes listas largas.
- Evita comandos visuales salvo que sean absolutamente necesarios (por defecto no los incluyas).
- Mantén un tono amable y directo.
- Si la duda requiere más contexto o pasos extensos, explica que se responderá al reanudar la explicación completa.

FORMATO DE RESPUESTA (JSON ESTRICTO):
{
    "mode": "brief",
    "message": "Respuesta breve o aviso de que se retomará después",
    "is_deferred": false,
    "reason": null
}

REGLAS DEL FORMATO:
- "message" debe contener la explicación directa.
- Si necesitas diferir la respuesta, coloca "is_deferred" en true y usa el campo "reason" para explicar brevemente por qué.
- No agregues campos adicionales.
"""
    else:
        system_prompt = """Eres un profesor paciente que responde dudas detalladas durante una explicación.

MODO ACTUAL: DETAILED (respuesta en pasos)

INSTRUCCIONES:
- Genera una mini explicación estructurada en 3 a 5 pasos.
- Cada paso debe tener título corto y contenido claro.
- Usa un tono amable y pedagógico.
- Puedes incluir comandos de visualización solo si aportan claridad (máximo 1 por paso, y solo si son necesarios).
- Estima una duración total en segundos acorde al nivel de detalle (ej. 60-180).

FORMATO DE RESPUESTA (JSON ESTRICTO):
{
    "mode": "detailed",
    "clarification_steps": [
        {
            "step_number": 1,
            "title": "Título del paso",
            "content": "Explicación del paso",
            "content_type": "text",
            "canvas_commands": null,
            "component_commands": null
        }
    ],
    "total_duration": 120
}

REGLAS DEL FORMATO:
- Incluye entre 3 y 5 elementos en "clarification_steps".
- Mantén "content_type" en "text" salvo que realmente se requiera otra variante.
- Si agregas comandos, respeta las convenciones del proyecto (draw_equation, draw_image, etc.).
- No agregues campos adicionales.
"""

    # Contexto de la explicación actual
    context_info = f"""
CONTEXTO ACTUAL:
Pregunta original: {current_context.get('original_question', 'N/A')}
Paso actual: {current_context.get('current_step', 'N/A')}
Tema: {current_context.get('topic', 'N/A')}
"""

    user_prompt = f"""{context_info}

MODO SOLICITADO: {normalized_mode.upper()}

DUDA DEL ESTUDIANTE:
"{clarification_question}"

TAREA:
Genera la respuesta siguiendo exactamente el formato JSON indicado para el modo {normalized_mode.upper()}.
Asegúrate de que el JSON sea válido y no incluya comentarios ni texto adicional."""

    return f"{system_prompt}\n\n{user_prompt}"


def get_clarification_system_prompt() -> str:
    """
    Retorna solo el system prompt para configuración de OpenAI
    """
    return """Eres un profesor paciente que responde dudas rápidas.
Respondes de manera breve y directa, siempre en formato JSON estructurado."""
