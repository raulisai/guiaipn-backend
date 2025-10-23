"""
Prompts para preguntas adicionales (follow-up) después de explicaciones
"""


def get_follow_up_prompt(
    follow_up_question: str,
    original_question: dict,
    previous_explanation: dict = None
) -> str:
    """
    Genera prompt para responder una pregunta adicional
    
    Args:
        follow_up_question: Pregunta adicional del usuario
        original_question: Pregunta de examen original
        previous_explanation: Explicación previa (opcional)
        
    Returns:
        str: Prompt completo para la IA
    """
    
    system_prompt = """Eres un profesor experto que profundiza en temas después de explicar una pregunta de examen.

IMPORTANTE:
- Esta es una pregunta ADICIONAL después de la explicación principal
- Proporciona una explicación COMPLETA y DETALLADA (3-5 pasos)
- Puedes usar canvas commands para visualizaciones
- Relaciona la respuesta con la pregunta de examen original
- Usa un tono pedagógico y motivador

FORMATO DE RESPUESTA (JSON):
{
    "answer_steps": [
        {
            "step_number": 1,
            "title": "Título del paso",
            "content": "Explicación detallada",
            "content_type": "text",
            "has_visual": false,
            "canvas_commands": null
        }
    ],
    "total_duration": 90
}

CANVAS COMMANDS - TIPOS SOPORTADOS:
1. draw_equation, 2. draw_image, 3. draw_graph, 4. draw_diagram, 5. draw_table, 6. highlight

COMPONENT COMMANDS - COMPONENTES INTERACTIVOS SVELTE:
1. image_modal - Modal con auto_close y duration
2. pdf_viewer - Visor PDF embebido
3. interactive_chart - Gráficas interactivas
4. video_player - Reproductor de video
5. interactive_3d - Modelos 3D rotables
6. quiz_component - Mini quizzes
7. code_editor - Editor de código
8. timeline_component - Líneas de tiempo

EJEMPLO:
{
    "step_number": 1,
    "canvas_commands": [{"command": "draw_equation", "parameters": {"equation": "x = 3", "description": "Solución"}}],
    "component_commands": [{"command": "image_component", "parameters": {"url": "url", "alt": "desc", "title": "título", "auto_close": true, "duration": 5000, "description": "modal"}}]
}

REGLAS: canvas_commands (visualizaciones estáticas), component_commands (componentes interactivos Svelte). Ambos pueden usarse juntos. auto_close + duration en ms. Siempre "description"
"""

    # Contexto de la pregunta original
    context_info = f"""
PREGUNTA DE EXAMEN ORIGINAL:
Materia: {original_question.get('subject', 'N/A')}
Tema: {original_question.get('topic', 'N/A')}
Pregunta: {original_question.get('question', '')}
Respuesta correcta: {original_question.get('correct_answer', '').upper()}
"""

    # Si hay explicación previa
    if previous_explanation:
        context_info += f"\n\nEXPLICACIÓN PREVIA:\n"
        steps = previous_explanation.get('explanation_steps', [])
        for step in steps[:2]:  # Solo primeros 2 pasos para contexto
            context_info += f"- {step.get('title', '')}\n"

    user_prompt = f"""{context_info}

PREGUNTA ADICIONAL DEL ESTUDIANTE:
"{follow_up_question}"

TAREA:
Responde esta pregunta adicional de manera completa y detallada.
- Usa 3-5 pasos
- Relaciona con la pregunta de examen original
- Incluye visualizaciones si ayudan a entender mejor
- Duración estimada: 60-120 segundos

Genera la respuesta en formato JSON como se especificó arriba."""

    return f"{system_prompt}\n\n{user_prompt}"


def get_follow_up_system_prompt() -> str:
    """
    Retorna solo el system prompt para configuración de OpenAI
    """
    return """Eres un profesor experto que profundiza en temas relacionados con exámenes de admisión.
Proporcionas explicaciones completas y detalladas, siempre en formato JSON estructurado."""
