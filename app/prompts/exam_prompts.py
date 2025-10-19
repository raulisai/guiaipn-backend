"""
Prompts para explicaciones de preguntas de examen
"""


def get_exam_question_prompt(question: dict, user_answer: str = None) -> str:
    """
    Genera prompt para explicar una pregunta de examen
    
    Args:
        question: Diccionario con datos de la pregunta
        user_answer: Respuesta del usuario (opcional)
        
    Returns:
        str: Prompt completo para la IA
    """
    
    system_prompt = """Eres un profesor experto en preparación para exámenes de admisión (IPN/UNAM).
Tu objetivo es explicar preguntas de examen de manera clara, paso a paso, usando un enfoque pedagógico.

IMPORTANTE:
- Explica como si estuvieras dibujando en un pizarrón
- Usa un tono amigable y motivador
- Divide la explicación en pasos claros y concisos
- Incluye comandos de canvas para visualizaciones cuando sea necesario
- Enfócate en el PROCESO, no solo en la respuesta

FORMATO DE RESPUESTA (JSON):
{
    "explanation_steps": [
        {
            "step_number": 1,
            "title": "Título del paso",
            "content": "Explicación detallada",
            "content_type": "text",
            "has_visual": false,
            "canvas_commands": null
        }
    ],
    "total_duration": 120
}

TIPOS DE CANVAS COMMANDS:
- "draw_equation": Para ecuaciones matemáticas
- "draw_graph": Para gráficas
- "draw_diagram": Para diagramas
- "highlight": Para resaltar partes importantes
"""

    # Construir contexto de la pregunta
    question_context = f"""
PREGUNTA DE EXAMEN:
Materia: {question.get('subject', 'N/A')}
Dificultad: {question.get('difficulty', 'medium')}
Tema: {question.get('topic', 'N/A')}

Pregunta: {question.get('question', '')}

Opciones:
"""
    
    # Agregar opciones
    options = question.get('options', {})
    for key, value in options.items():
        is_correct = key == question.get('correct_answer', '')
        marker = "✓" if is_correct else " "
        question_context += f"{marker} {key.upper()}) {value}\n"
    
    question_context += f"\nRespuesta correcta: {question.get('correct_answer', '').upper()}"
    
    # Si hay respuesta del usuario
    if user_answer:
        is_correct = user_answer.lower() == question.get('correct_answer', '').lower()
        if is_correct:
            question_context += f"\n\nEl estudiante respondió: {user_answer.upper()} ✓ (CORRECTO)"
        else:
            question_context += f"\n\nEl estudiante respondió: {user_answer.upper()} ✗ (INCORRECTO)"
    
    user_prompt = f"""{question_context}

TAREA:
Genera una explicación paso a paso de esta pregunta. Explica:
1. Qué conceptos se necesitan entender
2. Cómo abordar el problema
3. El proceso de solución paso a paso
4. Por qué la respuesta correcta es la correcta
5. Por qué las otras opciones son incorrectas (errores comunes)

Genera la respuesta en formato JSON como se especificó arriba.
Usa entre 3-5 pasos. Duración total estimada: 60-180 segundos."""

    return f"{system_prompt}\n\n{user_prompt}"


def get_exam_question_system_prompt() -> str:
    """
    Retorna solo el system prompt para configuración de OpenAI
    """
    return """Eres un profesor experto en preparación para exámenes de admisión (IPN/UNAM).
Explicas de manera clara, paso a paso, usando un enfoque pedagógico.
Siempre respondes en formato JSON estructurado."""
