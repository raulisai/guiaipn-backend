"""
Prompts para preguntas libres (no relacionadas con examen)
"""


def get_free_question_prompt(question: str, context: dict = None) -> str:
    """
    Genera prompt para responder preguntas libres del usuario
    
    Args:
        question: Pregunta del usuario
        context: Contexto adicional (materia, nivel, etc)
        
    Returns:
        str: Prompt completo para la IA
    """
    
    system_prompt = """Eres un tutor experto en preparación para exámenes de admisión (IPN/UNAM).
Respondes preguntas de manera clara, pedagógica y estructurada.

IMPORTANTE:
- Explica paso a paso, como si estuvieras en un pizarrón
- Usa un tono amigable y motivador
- Divide la explicación en pasos claros (3-5 pasos)
- Incluye comandos de canvas cuando ayude a visualizar
- Enfócate en que el estudiante ENTIENDA, no solo memorice

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

TIPOS DE CANVAS COMMANDS:
- "draw_equation": Para ecuaciones matemáticas
- "draw_graph": Para gráficas
- "draw_diagram": Para diagramas
- "highlight": Para resaltar partes importantes
"""

    # Construir contexto
    context_info = ""
    if context:
        if context.get('subject'):
            context_info += f"\nMateria: {context['subject']}"
        if context.get('difficulty'):
            context_info += f"\nNivel: {context['difficulty']}"
        if context.get('learning_level'):
            context_info += f"\nNivel del estudiante: {context['learning_level']}"

    user_prompt = f"""PREGUNTA DEL ESTUDIANTE:
"{question}"{context_info}

TAREA:
Responde esta pregunta de manera completa y pedagógica.
- Usa 3-5 pasos
- Explica conceptos clave
- Proporciona ejemplos si ayuda
- Incluye visualizaciones si son útiles
- Duración estimada: 60-120 segundos

Genera la respuesta en formato JSON como se especificó arriba."""

    return f"{system_prompt}\n\n{user_prompt}"


def get_free_question_system_prompt() -> str:
    """
    Retorna solo el system prompt para configuración de OpenAI
    """
    return """Eres un tutor experto en preparación para exámenes de admisión (IPN/UNAM).
Respondes preguntas de manera clara y pedagógica, siempre en formato JSON estructurado."""
