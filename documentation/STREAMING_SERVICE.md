# StreamingService + Socket.IO Handlers - Documentación

## Índice
1. [Arquitectura General](#arquitectura-general)
2. [Flujo ask_question](#flujo-ask_question)
3. [Flujo Pause/Resume](#flujo-pauseresume)
4. [Eventos Socket.IO](#eventos-socketio)
5. [Integración con Servicios](#integración-con-servicios)
6. [Ejemplos de Uso](#ejemplos-de-uso)
7. [Testing](#testing)

---

## Arquitectura General

### Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENTE (Frontend)                      │
│  - Socket.IO Client                                         │
│  - Event Listeners                                          │
│  - UI Components                                            │
└──────────────────────┬──────────────────────────────────────┘
                       │ WebSocket
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              SOCKET.IO HANDLERS (Backend)                    │
│  - app/socket_events/questions.py                           │
│    • ask_question                                           │
│    • pause_explanation                                      │
│    • resume_explanation                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Question     │ │ Streaming    │ │ Session      │
│ Service      │ │ Service      │ │ Service      │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ AI Service   │ │ AI Answers   │ │ Redis        │
│ (OpenAI)     │ │ Repository   │ │ (Sessions)   │
└──────────────┘ └──────────────┘ └──────────────┘
       │                │
       ▼                ▼
┌─────────────────────────────┐
│   Supabase (PostgreSQL)     │
│   - ai_answers table        │
└─────────────────────────────┘
```

---

## Flujo ask_question

### Diagrama de Secuencia Completo

```
Cliente          Socket.IO         QuestionService    AIService    StreamingService    Redis/DB
  │                  │                    │               │               │              │
  │─ask_question─────>│                   │               │               │              │
  │ {question,       │                    │               │               │              │
  │  context,        │                    │               │               │              │
  │  token}          │                    │               │               │              │
  │                  │                    │               │               │              │
  │                  │──verify_token──────>               │               │              │
  │                  │<─user_data─────────┘               │               │              │
  │                  │                    │               │               │              │
  │                  │──create_session────────────────────────────────────>│              │
  │                  │                    │               │               │──save──────>│
  │                  │<─session_id────────────────────────────────────────┘<─OK─────────┘
  │                  │                    │               │               │              │
  │                  │──process_question──>               │               │              │
  │                  │                    │──normalize────>               │              │
  │                  │                    │──hash─────────>               │              │
  │                  │                    │──check_cache──────────────────────────────>│
  │                  │                    │<─cached_answer────────────────────────────┘│
  │                  │                    │               │               │              │
  │                  │                    │               │               │              │
  ├─ CASO 1: RESPUESTA EN CACHE ─────────────────────────────────────────────────────────┤
  │                  │                    │               │               │              │
  │                  │<─result (cached)───┘               │               │              │
  │                  │                    │               │               │              │
  │                  │──start_streaming───────────────────────────────────>│              │
  │                  │  {answer_data,     │               │               │              │
  │                  │   session_id}      │               │               │              │
  │                  │                    │               │               │──update────>│
  │                  │                    │               │               │  streaming  │
  │<─explanation_start│<───────────────────────────────────────────────────┘  state     │
  │ {total_steps,    │                    │               │               │              │
  │  duration}       │                    │               │               │              │
  │                  │                    │               │               │              │
  │<─step_start──────│<───────────────────────────────────────────────────┐              │
  │ {step, title}    │                    │               │               │              │
  │                  │                    │               │               │              │
  │<─content_chunk───│<───────────────────────────────────────────────────┤              │
  │ {chunk, pos}     │                    │               │               │              │
  │                  │                    │               │               │              │
  │<─content_chunk───│<───────────────────────────────────────────────────┤              │
  │ {chunk, pos}     │                    │               │               │              │
  │                  │                    │               │               │              │
  │<─canvas_command──│<───────────────────────────────────────────────────┤              │
  │ {command}        │                    │               │               │              │
  │                  │                    │               │               │              │
  │<─step_complete───│<───────────────────────────────────────────────────┤              │
  │ {step}           │                    │               │               │              │
  │                  │                    │               │               │              │
  │<─explanation_────│<───────────────────────────────────────────────────┘              │
  │  complete        │                    │               │               │              │
  │                  │                    │               │               │              │
  │                  │                    │               │               │              │
  ├─ CASO 2: GENERAR CON IA ─────────────────────────────────────────────────────────────┤
  │                  │                    │               │               │              │
  │                  │<─result (no cache)─┘               │               │              │
  │                  │                    │               │               │              │
  │<─waiting_phrase──│                    │               │               │              │
  │ "Analizando..."  │                    │               │               │              │
  │                  │                    │               │               │              │
  │                  │──generate_answer───────────────────>│               │              │
  │                  │  {question,        │               │               │              │
  │                  │   context}         │               │               │              │
  │                  │                    │               │──OpenAI API──>│              │
  │                  │                    │               │<─JSON response┘              │
  │                  │                    │               │               │              │
  │                  │<─ai_response───────────────────────┘               │              │
  │                  │  {steps,           │               │               │              │
  │                  │   duration}        │               │               │              │
  │                  │                    │               │               │              │
  │                  │──save_answer───────────────────────────────────────────────────>│
  │                  │                    │               │               │  ai_answers │
  │                  │<─saved_id──────────────────────────────────────────────────────┘│
  │                  │                    │               │               │              │
  │                  │──start_streaming───────────────────────────────────>│              │
  │                  │                    │               │               │              │
  │<─explanation_start│<───────────────────────────────────────────────────┘              │
  │  ... (igual que caso 1)              │               │               │              │
  │                  │                    │               │               │              │
```

### Flujo Simplificado

#### 1. Respuesta en Cache
```
┌─────────┐
│ Cliente │
└────┬────┘
     │
     │ ask_question
     ▼
┌──────────────┐
│ Socket.IO    │
│ Handler      │
└────┬─────────┘
     │
     │ 1. Verificar auth
     │ 2. Crear/obtener sesión
     │ 3. Procesar pregunta
     ▼
┌──────────────┐      ┌─────────┐
│ Question     │─────>│ Cache   │
│ Service      │<─────│ (DB)    │
└────┬─────────┘      └─────────┘
     │ ✓ Encontrado
     ▼
┌──────────────┐
│ Streaming    │
│ Service      │
└────┬─────────┘
     │
     │ explanation_start
     │ step_start
     │ content_chunk (x N)
     │ canvas_command (si hay)
     │ step_complete
     │ explanation_complete
     ▼
┌─────────┐
│ Cliente │
└─────────┘
```

#### 2. Generar con IA
```
┌─────────┐
│ Cliente │
└────┬────┘
     │
     │ ask_question
     ▼
┌──────────────┐
│ Socket.IO    │
│ Handler      │
└────┬─────────┘
     │
     │ 1. Verificar auth
     │ 2. Crear/obtener sesión
     │ 3. Procesar pregunta
     ▼
┌──────────────┐      ┌─────────┐
│ Question     │─────>│ Cache   │
│ Service      │<─────│ (DB)    │
└────┬─────────┘      └─────────┘
     │ ✗ No encontrado
     │
     │ waiting_phrase
     ▼
┌──────────────┐      ┌─────────┐
│ AI Service   │─────>│ OpenAI  │
│              │<─────│ API     │
└────┬─────────┘      └─────────┘
     │ JSON response
     │
     │ Guardar en DB
     ▼
┌──────────────┐
│ Streaming    │
│ Service      │
└────┬─────────┘
     │
     │ (igual que cache)
     ▼
┌─────────┐
│ Cliente │
└─────────┘
```

---

## Flujo Pause/Resume

### Diagrama de Secuencia

```
Cliente          Socket.IO         StreamingService    SessionService    Redis
  │                  │                    │                  │             │
  │                  │                    │                  │             │
  ├─ STREAMING ACTIVO ───────────────────────────────────────────────────────┤
  │                  │                    │                  │             │
  │<─content_chunk───│<───────────────────┤                  │             │
  │                  │                    │                  │             │
  │<─content_chunk───│<───────────────────┤                  │             │
  │                  │                    │                  │             │
  │                  │                    │                  │             │
  ├─ USUARIO PAUSA ──────────────────────────────────────────────────────────┤
  │                  │                    │                  │             │
  │─pause_explanation>│                   │                  │             │
  │                  │                    │                  │             │
  │                  │──pause_streaming───────────────────────>│             │
  │                  │  {session_id,      │                  │             │
  │                  │   position}        │                  │             │
  │                  │                    │                  │──update───>│
  │                  │                    │                  │  is_paused │
  │                  │                    │                  │  pause_pos │
  │                  │                    │                  │<─OK────────┘
  │                  │<───────────────────────────────────────┘             │
  │                  │                    │                  │             │
  │<─explanation_────│                    │                  │             │
  │  paused          │                    │                  │             │
  │                  │                    │                  │             │
  │                  │                    │──check_paused────>│             │
  │                  │                    │<─is_paused=True──┘             │
  │                  │                    │                  │             │
  │                  │                    │ (detiene chunks) │             │
  │                  │                    │                  │             │
  │                  │                    │                  │             │
  ├─ USUARIO REANUDA ────────────────────────────────────────────────────────┤
  │                  │                    │                  │             │
  │─resume_──────────>│                   │                  │             │
  │  explanation     │                    │                  │             │
  │                  │                    │                  │             │
  │                  │──get_session───────────────────────────>│             │
  │                  │                    │                  │──get──────>│
  │                  │<─session_data──────────────────────────┘<─data─────┘
  │                  │  {pause_position,  │                  │             │
  │                  │   current_step}    │                  │             │
  │                  │                    │                  │             │
  │                  │──resume_streaming──>                  │             │
  │                  │  {session_id,      │                  │             │
  │                  │   answer_data}     │                  │             │
  │                  │                    │                  │             │
  │                  │                    │──resume──────────>│             │
  │                  │                    │                  │──update───>│
  │                  │                    │                  │  is_paused │
  │                  │                    │                  │  =false    │
  │                  │                    │                  │<─OK────────┘
  │                  │                    │<─────────────────┘             │
  │                  │                    │                  │             │
  │<─streaming_resumed│<───────────────────┤                  │             │
  │ {step, position} │                    │                  │             │
  │                  │                    │                  │             │
  │<─content_chunk───│<───────────────────┤                  │             │
  │ (desde position) │                    │                  │             │
  │                  │                    │                  │             │
  │<─content_chunk───│<───────────────────┤                  │             │
  │                  │                    │                  │             │
  │<─step_complete───│<───────────────────┤                  │             │
  │                  │                    │                  │             │
  │<─explanation_────│<───────────────────┘                  │             │
  │  complete        │                    │                  │             │
  │                  │                    │                  │             │
```

### Estados de Sesión en Redis

```
┌─────────────────────────────────────┐
│  session:{session_id}               │
├─────────────────────────────────────┤
│  user_id: "uuid"                    │
│  connection_id: "socket_id"         │
│  current_question: "hash_sha256"    │
│  current_step: 2                    │
│  pause_position: 150                │
│  is_paused: true                    │
│  is_streaming: true                 │
│  created_at: "2025-01-19T..."       │
│  last_activity: "2025-01-19T..."    │
└─────────────────────────────────────┘
         │
         │ TTL: 1800s (30 min)
         │ Auto-renewed on activity
         ▼
```

---

## Eventos Socket.IO

### Eventos del Cliente → Servidor

| Evento | Payload | Descripción |
|--------|---------|-------------|
| `ask_question` | `{token, question, context}` | Hacer una pregunta |
| `pause_explanation` | `{token}` | Pausar streaming |
| `resume_explanation` | `{token, answer_data?}` | Reanudar streaming |

### Eventos del Servidor → Cliente

| Evento | Payload | Cuándo se emite |
|--------|---------|-----------------|
| `waiting_phrase` | `{message}` | Generando con IA |
| `explanation_start` | `{total_steps, estimated_duration, question_hash}` | Inicio de streaming |
| `step_start` | `{step, title, type}` | Inicio de cada paso |
| `content_chunk` | `{step, chunk, position, is_final}` | Cada chunk de contenido |
| `canvas_command` | `{step, command}` | Comando de visualización |
| `step_complete` | `{step}` | Fin de paso |
| `explanation_complete` | `{total_duration, steps_completed}` | Fin de streaming |
| `streaming_paused` | `{step, message}` | Streaming pausado |
| `streaming_resumed` | `{step, position}` | Streaming reanudado |
| `error` | `{code, message}` | Error |

---

## Integración con Servicios

### QuestionService
```python
# Valida, normaliza, genera hash, busca en cache
result = question_service.process_question(user_id, question_text)

# Retorna:
{
    "question_hash": "sha256...",
    "question_text": "texto original",
    "normalized_text": "texto normalizado",
    "answer_id": "uuid" | None,
    "cached": True | False,
    "answer_steps": [...],  # Si cached
    "total_duration": 60    # Si cached
}
```

### AIService
```python
# Genera respuesta estructurada con OpenAI
ai_response = ai_service.generate_answer(question_text, context)

# Retorna:
{
    "steps": [
        {
            "title": "Título",
            "type": "text|math|image",
            "content": "Contenido",
            "canvas_commands": [...]
        }
    ],
    "total_duration": 120
}
```

### StreamingService
```python
# Inicia streaming progresivo
streaming_service.start_streaming(answer_data, session_id)

# Pausa/Resume
streaming_service.resume_streaming(session_id, answer_data)
```

### SessionService
```python
# Gestión de sesiones en Redis
session_id = session_service.create_session(user_id, connection_id)
session_service.pause_streaming(session_id, position)
session_service.resume_streaming(session_id)
```

---

## Ejemplos de Uso

### Cliente JavaScript

```javascript
import io from 'socket.io-client';

// Conectar
const socket = io('http://localhost:5000');

// Hacer pregunta
function askQuestion(question, context = {}) {
    const token = localStorage.getItem('jwt_token');
    
    socket.emit('ask_question', {
        token: token,
        question: question,
        context: context
    });
}

// Escuchar eventos
socket.on('waiting_phrase', (data) => {
    showLoadingMessage(data.message);
});

socket.on('explanation_start', (data) => {
    initializeExplanation(data.total_steps, data.estimated_duration);
});

socket.on('step_start', (data) => {
    createStepContainer(data.step, data.title, data.type);
});

socket.on('content_chunk', (data) => {
    appendChunkToStep(data.step, data.chunk);
    
    if (data.is_final) {
        finalizeStepContent(data.step);
    }
});

socket.on('canvas_command', (data) => {
    executeCanvasCommand(data.step, data.command);
});

socket.on('step_complete', (data) => {
    markStepComplete(data.step);
});

socket.on('explanation_complete', (data) => {
    showCompletionMessage(data.total_duration);
});

// Pausar
function pauseExplanation() {
    const token = localStorage.getItem('jwt_token');
    socket.emit('pause_explanation', { token });
}

// Reanudar
function resumeExplanation() {
    const token = localStorage.getItem('jwt_token');
    socket.emit('resume_explanation', { token });
}

socket.on('streaming_paused', (data) => {
    showPauseButton(false);
    showResumeButton(true);
});

socket.on('streaming_resumed', (data) => {
    showPauseButton(true);
    showResumeButton(false);
});

socket.on('error', (data) => {
    showError(data.code, data.message);
});
```

### Cliente React

```jsx
import { useEffect, useState } from 'react';
import io from 'socket.io-client';

function QuestionInterface() {
    const [socket, setSocket] = useState(null);
    const [steps, setSteps] = useState([]);
    const [isStreaming, setIsStreaming] = useState(false);
    const [isPaused, setIsPaused] = useState(false);
    
    useEffect(() => {
        const newSocket = io('http://localhost:5000');
        setSocket(newSocket);
        
        // Eventos
        newSocket.on('explanation_start', (data) => {
            setSteps([]);
            setIsStreaming(true);
        });
        
        newSocket.on('step_start', (data) => {
            setSteps(prev => [...prev, {
                step: data.step,
                title: data.title,
                type: data.type,
                content: ''
            }]);
        });
        
        newSocket.on('content_chunk', (data) => {
            setSteps(prev => prev.map(step => 
                step.step === data.step
                    ? { ...step, content: step.content + data.chunk }
                    : step
            ));
        });
        
        newSocket.on('explanation_complete', () => {
            setIsStreaming(false);
        });
        
        newSocket.on('streaming_paused', () => {
            setIsPaused(true);
        });
        
        newSocket.on('streaming_resumed', () => {
            setIsPaused(false);
        });
        
        return () => newSocket.close();
    }, []);
    
    const askQuestion = (question) => {
        const token = localStorage.getItem('jwt_token');
        socket.emit('ask_question', {
            token,
            question,
            context: { subject: 'física' }
        });
    };
    
    const pause = () => {
        const token = localStorage.getItem('jwt_token');
        socket.emit('pause_explanation', { token });
    };
    
    const resume = () => {
        const token = localStorage.getItem('jwt_token');
        socket.emit('resume_explanation', { token });
    };
    
    return (
        <div>
            <input 
                type="text" 
                onKeyPress={(e) => {
                    if (e.key === 'Enter') askQuestion(e.target.value);
                }}
            />
            
            {isStreaming && (
                <button onClick={isPaused ? resume : pause}>
                    {isPaused ? 'Reanudar' : 'Pausar'}
                </button>
            )}
            
            {steps.map(step => (
                <div key={step.step}>
                    <h3>{step.title}</h3>
                    <p>{step.content}</p>
                </div>
            ))}
        </div>
    );
}
```

---

## Testing

### Ejecutar Tests

```bash
# Todos los tests de socket
python -m pytest tests/unit/test_socket_questions.py -v

# Test específico
python -m pytest tests/unit/test_socket_questions.py::TestAskQuestionHandler::test_ask_question_cached_answer -v

# Con coverage
python -m pytest tests/unit/test_socket_questions.py --cov=app.socket_events --cov=app.services.streaming_service
```

### Estructura de Tests

```python
# tests/unit/test_socket_questions.py

class TestAskQuestionHandler:
    """Tests para ask_question"""
    - test_ask_question_cached_answer
    - test_ask_question_generate_with_ai

class TestPauseResumeHandlers:
    """Tests para pause/resume"""
    - test_pause_explanation
    - test_resume_explanation

class TestStreamingService:
    """Tests para StreamingService"""
    - test_start_streaming
    - test_stream_with_canvas_commands
    - test_pause_during_streaming

class TestIntegration:
    """Tests de integración"""
    - test_full_cached_flow
    - test_full_ai_generation_flow
```

---

## Configuración

### Variables de Entorno

```bash
# .env
OPENAI_API_KEY=sk-...
REDIS_URL=redis://localhost:6379/0
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=...
```

### Configuración de Streaming

```python
# app/services/streaming_service.py

CHUNK_SIZE = 50  # Caracteres por chunk
CHUNK_DELAY = 0.05  # Segundos entre chunks
```

### Configuración de Sesión

```python
# app/services/session_service.py

DEFAULT_TTL = 1800  # 30 minutos
```

---

## Troubleshooting

### Problema: Streaming no inicia

**Síntomas:** Cliente no recibe eventos después de `ask_question`

**Solución:**
1. Verificar autenticación (token válido)
2. Verificar conexión Socket.IO
3. Revisar logs del servidor
4. Verificar que Redis está corriendo

### Problema: Pause/Resume no funciona

**Síntomas:** Pause no detiene el streaming

**Solución:**
1. Verificar que existe sesión activa
2. Revisar estado en Redis: `redis-cli GET session:{session_id}`
3. Verificar que `is_paused` se actualiza correctamente

### Problema: Canvas commands no se ejecutan

**Síntomas:** Visualizaciones no aparecen

**Solución:**
1. Verificar que el step tiene `canvas_commands`
2. Implementar handler de `canvas_command` en cliente
3. Verificar formato de comandos

---

## Métricas y Monitoreo

### Logs Importantes

```python
# Pregunta procesada
print(f"✓ Pregunta procesada para usuario: {user.get('email')}")

# Respuesta en cache
print(f"✓ Respuesta en cache para: {question_text[:50]}...")

# Generando con IA
print(f"🤖 Generando respuesta con IA para: {question_text[:50]}...")

# Streaming pausado
print(f"⏸ Streaming pausado para sesión: {session_id}")

# Streaming reanudado
print(f"▶ Streaming reanudado para sesión: {session_id}")
```

### Eventos a Monitorear

- Tiempo de respuesta de OpenAI
- Tasa de cache hit/miss
- Número de pausas por sesión
- Duración promedio de streaming
- Errores de generación IA

---

## Próximos Pasos

- [ ] Implementar rate limiting
- [ ] Implementar consume_credits
- [ ] Agregar métricas con Prometheus
- [ ] Optimizar chunk_size dinámico
- [ ] Soporte para múltiples idiomas
- [ ] Compresión de eventos Socket.IO
- [ ] Retry automático en errores de IA
- [ ] Queue para generación IA (Celery)

---

## Referencias

- [Flask-SocketIO Documentation](https://flask-socketio.readthedocs.io/)
- [Socket.IO Client API](https://socket.io/docs/v4/client-api/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Redis Commands](https://redis.io/commands/)

Archivos Creados/Modificados
Archivo	Descripción	Estado
app/services/streaming_service.py
Servicio de streaming en tiempo real	✅
app/socket_events/questions.py
Handlers Socket.IO completos	✅
app/services/ai_service.py
Integración con OpenAI	✅
app/services/question_service.py
Procesamiento de preguntas	✅
app/utils/text_processing.py
Normalización y hash	✅
tests/unit/test_socket_questions.py
Tests Socket.IO (9 tests)	✅
tests/unit/test_ai_service.py
Tests AIService (27 tests)	✅
tests/unit/test_question_service.py
Tests QuestionService (23 tests)	✅
tests/unit/test_text_processing.py
Tests text utils (24 tests)	✅
requirements.txt
pytest-socketio agregado	✅
documentation/STREAMING_SERVICE.md
Documentación completa	✅
Tests Totales: 83 tests pasando ✓