"""
Prompts para aclaraciones rápidas durante explicaciones
"""


def get_clarification_prompt(
    clarification_question: str,
    current_context: dict
) -> str:
    """
    Genera prompt para responder una interrupción/aclaración
    
    Args:
        clarification_question: Pregunta del usuario
        current_context: Contexto actual (pregunta original, paso actual, etc)
        
    Returns:
        str: Prompt completo para la IA
    """
    
    system_prompt = """Eres un profesor paciente que responde dudas rápidas durante una explicación.

IMPORTANTE:
- Responde de manera BREVE y DIRECTA (1-2 pasos máximo)
- Usa canvas_commands/component_commands SOLO si es absolutamente necesario
- Mantén el foco en la duda específica
- Usa un tono amigable y alentador
- Después de responder, el estudiante continuará con la explicación principal

FORMATO DE RESPUESTA (JSON):
{
    "clarification_steps": [
        {
            "step_number": 1,
            "title": "Respuesta breve",
            "content": "Explicación concisa",
            "content_type": "text",
            "has_visual": false,
            "canvas_commands": null
        }
    ],
    "total_duration": 15
}

CANVAS COMMANDS: draw_equation, draw_image, draw_graph, draw_diagram, draw_table, highlight
COMPONENT COMMANDS: image_modal, pdf_viewer, interactive_chart, video_player, interactive_3d, quiz_component, code_editor, timeline_component

USO LIMITADO: Solo si mejora significativamente la claridad. Máximo 1-2 comandos.
EJEMPLO: {"canvas_commands": [{"command": "draw_equation", "parameters": {"equation": "x=3", "description": "Solución"}}], "component_commands": null}
"""

    # Contexto de la explicación actual
    context_info = f"""
CONTEXTO ACTUAL:
Pregunta original: {current_context.get('original_question', 'N/A')}
Paso actual: {current_context.get('current_step', 'N/A')}
Tema: {current_context.get('topic', 'N/A')}
"""

    user_prompt = f"""{context_info}

DUDA DEL ESTUDIANTE:
"{clarification_question}"

TAREA:
Responde esta duda de manera breve (1-2 pasos, máximo 30 segundos).
Mantén la respuesta enfocada y simple.
Genera la respuesta en formato JSON como se especificó arriba."""

    return f"{system_prompt}\n\n{user_prompt}"


def get_clarification_system_prompt() -> str:
    """
    Retorna solo el system prompt para configuración de OpenAI
    """
    return """Eres un profesor paciente que responde dudas rápidas.
Respondes de manera breve y directa, siempre en formato JSON estructurado."""
