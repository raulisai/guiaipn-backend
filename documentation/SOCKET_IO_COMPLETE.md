# 🔌 Socket.IO - Documentación Completa

## Conexión al Servidor

### URL del Servidor
```
ws://localhost:5000
```

### Inicialización del Cliente

```javascript
import io from 'socket.io-client';

const socket = io('http://localhost:5000', {
  auth: {
    token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' // JWT de Supabase
  },
  transports: ['websocket'],
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionAttempts: 5
});
```

---

## 📡 Eventos del Ciclo de Vida

### connect (Automático)
Se dispara cuando el cliente se conecta exitosamente.

```javascript
socket.on('connect', () => {
  console.log('Conectado al servidor');
  console.log('Socket ID:', socket.id);
});
```

**Flujo Backend:**
1. Valida token JWT en `auth.token`
2. Crea sesión en Redis con UUID
3. Mapea `socket.id` → `session_id`
4. Emite `connection_established`

---

### connection_established
Confirmación de conexión exitosa con datos de sesión.

```javascript
socket.on('connection_established', (data) => {
  console.log('Sesión creada:', data);
  // Guardar session_id para uso posterior
  localStorage.setItem('session_id', data.session_id);
});
```

**Payload:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_info": {
    "email": "user@example.com",
    "id": "user-uuid"
  }
}
```

---

### disconnect (Automático)
Se dispara cuando el cliente se desconecta.

```javascript
socket.on('disconnect', (reason) => {
  console.log('Desconectado:', reason);
  
  if (reason === 'io server disconnect') {
    // El servidor forzó la desconexión (ej: token inválido)
    // Redirigir a login
  } else {
    // Desconexión normal o error de red
    // Socket.IO reintentará automáticamente
  }
});
```

**Flujo Backend:**
1. Obtiene `session_id` del mapeo
2. Elimina sesión de Redis
3. Limpia mapeo `socket.id` → `session_id`

---

### error
Errores generales del servidor.

```javascript
socket.on('error', (error) => {
  console.error('Error:', error);
  
  switch(error.code) {
    case 'AUTH_REQUIRED':
      // Token no proporcionado
      redirectToLogin();
      break;
    case 'AUTH_FAILED':
      // Token inválido o expirado
      refreshTokenAndReconnect();
      break;
    case 'VALIDATION_ERROR':
      // Datos inválidos
      showErrorToUser(error.message);
      break;
    case 'AI_GENERATION_ERROR':
      // Error generando respuesta
      showRetryOption();
      break;
    default:
      showGenericError();
  }
});
```

**Códigos de Error:**
- `AUTH_REQUIRED`: Token no proporcionado
- `AUTH_FAILED`: Autenticación fallida
- `INVALID_PAYLOAD`: Payload inválido
- `VALIDATION_ERROR`: Error de validación
- `AI_GENERATION_ERROR`: Error generando respuesta IA
- `SESSION_NOT_FOUND`: Sesión no encontrada
- `PROCESSING_ERROR`: Error procesando solicitud
- `NO_SESSION`: No hay sesión activa
- `PAUSE_ERROR`: Error pausando
- `RESUME_ERROR`: Error reanudando

---

## 💬 Preguntas Libres (ask_question)

### Flujo Completo

```
┌──────────┐                ┌──────────┐                ┌──────────┐
│ Frontend │                │  Backend │                │   Redis  │
└────┬─────┘                └────┬─────┘                └────┬─────┘
     │                           │                           │
     │ 1. ask_question           │                           │
     ├──────────────────────────→│                           │
     │                           │                           │
     │                           │ 2. Validar + normalizar   │
     │                           │                           │
     │                           │ 3. Buscar en cache (DB)   │
     │                           │                           │
     │ 4a. Si no cached:         │                           │
     │     waiting_phrase        │                           │
     │←──────────────────────────┤                           │
     │                           │                           │
     │                           │ 5. Generar con OpenAI     │
     │                           │                           │
     │                           │ 6. Guardar en DB          │
     │                           │                           │
     │ 7. explanation_start      │                           │
     │←──────────────────────────┤                           │
     │                           │                           │
     │ 8. step_start             │                           │
     │←──────────────────────────┤                           │
     │                           │                           │
     │ 9. content_chunk (x N)    │                           │
     │←──────────────────────────┤                           │
     │                           │                           │
     │ 10. canvas_command        │                           │
     │←──────────────────────────┤                           │
     │                           │                           │
     │ 11. step_complete         │                           │
     │←──────────────────────────┤                           │
     │                           │                           │
     │ [Repetir 8-11 para cada paso]                         │
     │                           │                           │
     │ 12. explanation_complete  │                           │
     │←──────────────────────────┤                           │
```

### 1. ask_question (Cliente → Servidor)

```javascript
socket.emit('ask_question', {
  token: 'jwt_token',
  question: '¿Qué es la energía cinética?',
  context: {
    subject: 'fisica',
    difficulty: 'medium',
    previous_questions: [] // Opcional
  }
});
```

**Validaciones Backend:**
- Longitud mínima: 5 caracteres
- Longitud máxima: 1000 caracteres
- Token JWT válido

---

### 2. waiting_phrase (Servidor → Cliente)

Emitido solo si la respuesta no está en cache y se debe generar con IA.

```javascript
socket.on('waiting_phrase', (data) => {
  showLoadingMessage(data.message);
});
```

**Payload:**
```json
{
  "message": "Analizando tu pregunta..."
}
```

**Frases posibles:**
- "Analizando tu pregunta..."
- "Consultando la base de conocimiento..."
- "Preparando una explicación detallada..."
- "Organizando los pasos de la solución..."

---

### 3. explanation_start (Servidor → Cliente)

Metadata inicial de la explicación.

```javascript
socket.on('explanation_start', (data) => {
  initializeExplanationUI(data);
  startProgressBar(data.estimated_duration);
});
```

**Payload:**
```json
{
  "total_steps": 4,
  "estimated_duration": 120,
  "question_hash": "sha256_hash_of_normalized_question"
}
```

---

### 4. step_start (Servidor → Cliente)

Inicio de cada paso de la explicación.

```javascript
socket.on('step_start', (data) => {
  createStepContainer(data.step);
  setStepTitle(data.step, data.title);
  setStepType(data.step, data.type);
});
```

**Payload:**
```json
{
  "step": 0,
  "title": "Definición de Energía Cinética",
  "type": "text"
}
```

**Tipos de paso:**
- `text`: Explicación textual
- `math`: Fórmulas matemáticas (LaTeX)
- `image`: Descripción de diagrama

---

### 5. content_chunk (Servidor → Cliente)

Contenido del paso en chunks (efecto typewriter).

```javascript
let stepContent = {};

socket.on('content_chunk', (data) => {
  if (!stepContent[data.step]) {
    stepContent[data.step] = '';
  }
  
  stepContent[data.step] += data.chunk;
  updateStepContent(data.step, stepContent[data.step]);
  
  if (data.is_final) {
    finalizeStepContent(data.step);
  }
});
```

**Payload:**
```json
{
  "step": 0,
  "chunk": "La energía cinética es la energía que posee",
  "position": 0,
  "is_final": false
}
```

**Características:**
- Chunks de ~50 caracteres
- Delay de 50ms entre chunks
- `is_final: true` en el último chunk

---

### 6. canvas_command (Servidor → Cliente)

Comandos para visualizaciones en canvas.

```javascript
socket.on('canvas_command', (data) => {
  executeCanvasCommand(data.step, data.command);
});
```

**Payload:**
```json
{
  "step": 1,
  "command": {
    "type": "draw_axis",
    "x": 50,
    "y": 200,
    "color": "#333"
  }
}
```

**Tipos de comando:**
- `draw_axis`: Dibujar ejes coordenados
- `plot_function`: Graficar función matemática
- `draw_triangle`: Dibujar triángulo
- `draw_circle`: Dibujar círculo
- `draw_vector`: Dibujar vector
- `add_label`: Agregar etiqueta

**Ejemplo de implementación:**
```javascript
function executeCanvasCommand(step, command) {
  const canvas = document.getElementById(`canvas-step-${step}`);
  const ctx = canvas.getContext('2d');
  
  switch(command.type) {
    case 'draw_axis':
      ctx.beginPath();
      ctx.moveTo(command.x, 0);
      ctx.lineTo(command.x, canvas.height);
      ctx.moveTo(0, command.y);
      ctx.lineTo(canvas.width, command.y);
      ctx.strokeStyle = command.color || '#333';
      ctx.stroke();
      break;
    
    case 'plot_function':
      // Implementar graficación de función
      break;
    
    // ... otros comandos
  }
}
```

---

### 7. step_complete (Servidor → Cliente)

Fin de un paso individual.

```javascript
socket.on('step_complete', (data) => {
  markStepAsComplete(data.step);
  scrollToNextStep(data.step + 1);
});
```

**Payload:**
```json
{
  "step": 0
}
```

---

### 8. explanation_complete (Servidor → Cliente)

Fin de toda la explicación.

```javascript
socket.on('explanation_complete', (data) => {
  stopProgressBar();
  showCompletionMessage();
  enableFeedbackButtons();
  showFollowUpOptions();
});
```

**Payload:**
```json
{
  "total_duration": 120,
  "steps_completed": 4
}
```

---

## ⏸️ Control de Reproducción

### pause_explanation (Cliente → Servidor)

```javascript
function pauseExplanation() {
  socket.emit('pause_explanation', {
    token: 'jwt_token'
  });
}
```

**Respuesta:**
```javascript
socket.on('explanation_paused', (data) => {
  showPauseIcon();
  enableResumeButton();
});
```

**Payload:**
```json
{
  "message": "Explicación pausada",
  "session_id": "uuid"
}
```

---

### resume_explanation (Cliente → Servidor)

```javascript
function resumeExplanation() {
  socket.emit('resume_explanation', {
    token: 'jwt_token',
    answer_data: null // Se recupera de sesión si es null
  });
}
```

**Respuestas:**
```javascript
socket.on('streaming_resumed', (data) => {
  showPlayIcon();
  disableResumeButton();
  // Continúa con content_chunk, step_complete, etc.
});

socket.on('streaming_paused', (data) => {
  // Si se pausó durante el resume
});
```

**Payload:**
```json
{
  "step": 2,
  "position": 150
}
```

---

## 📚 Explicaciones de Examen

### start_explanation (Cliente → Servidor)

Solicita explicación de una pregunta de examen.

```javascript
socket.emit('start_explanation', {
  question_id: 'uuid-of-exam-question',
  user_answer: 'a' // Opcional: respuesta del usuario
});
```

**Flujo:**
1. Backend busca explicación existente en DB
2. Si no existe, genera con IA
3. Guarda en `exam_explanations` table
4. Inicia streaming

**Respuestas:**
```javascript
// Si no existe en cache:
socket.on('waiting_phrase', (data) => {
  // { phrase: "Generando explicación...", category: "generating", estimated_time: 3000 }
});

socket.on('explanation_start', (data) => {
  // {
  //   explanation_id: "uuid",
  //   question_id: "uuid",
  //   total_steps: 5,
  //   estimated_duration: 90
  // }
});

// Luego: step_start, content_chunk, step_complete, explanation_complete
```

---

### explanation_feedback (Cliente → Servidor)

Registra feedback del usuario sobre una explicación.

```javascript
function submitFeedback(explanationId, isHelpful, flagReason = null) {
  socket.emit('explanation_feedback', {
    explanation_id: explanationId,
    is_helpful: isHelpful,
    flag_reason: flagReason // "incorrect", "unclear", "incomplete"
  });
}
```

**Respuesta:**
```javascript
socket.on('feedback_recorded', (data) => {
  showThankYouMessage();
});
```

**Payload:**
```json
{
  "explanation_id": "uuid",
  "success": true
}
```

---

## 🔄 Preguntas Adicionales (Follow-ups)

### ask_follow_up_question (Cliente → Servidor)

Hace una pregunta adicional relacionada con una pregunta de examen.

```javascript
socket.emit('ask_follow_up_question', {
  question: '¿Cómo se calcula la energía cinética en movimiento circular?',
  related_to: 'uuid-of-original-question'
});
```

**Respuestas:**
```javascript
socket.on('follow_up_start', (data) => {
  // {
  //   answer_id: "uuid",
  //   total_steps: 3,
  //   estimated_duration: 90,
  //   is_follow_up: true
  // }
});

// Luego: step_start, content_chunk, step_complete

socket.on('follow_up_complete', (data) => {
  // {
  //   answer_id: "uuid",
  //   total_duration: 90,
  //   steps_completed: 3
  // }
});

socket.on('follow_up_options', (data) => {
  // { options: ['more_questions', 'finish'] }
  showFollowUpOptions(data.options);
});
```

---

## 🚨 Interrupciones y Aclaraciones

### interrupt_explanation (Cliente → Servidor)

Interrumpe la explicación actual para hacer una aclaración rápida.

```javascript
socket.emit('interrupt_explanation', {
  clarification_question: '¿Qué significa "masa en reposo"?',
  current_context: {
    current_step: 2,
    topic: 'Energía Cinética'
  }
});
```

**Respuestas:**
```javascript
socket.on('clarification_start', (data) => {
  // { is_brief: true, estimated_duration: 15 }
  pauseMainExplanation();
  showClarificationModal();
});

socket.on('clarification_chunk', (data) => {
  // {
  //   step_number: 1,
  //   title: "Masa en Reposo",
  //   content: "...",
  //   content_type: "text"
  // }
  appendToClarificationModal(data);
});

socket.on('clarification_complete', (data) => {
  // { total_duration: 15 }
  showContinueOptions();
});

socket.on('clarification_options', (data) => {
  // { options: ['continue', 'new_question'] }
  showOptions(data.options);
});
```

**Para continuar:**
```javascript
socket.emit('resume_explanation', {});

socket.on('explanation_resumed', (data) => {
  closeClarificationModal();
  resumeMainExplanation();
});
```

---

## 🎯 Ejemplo Completo de Implementación

```javascript
import io from 'socket.io-client';

class GuiaIPNSocket {
  constructor(token) {
    this.token = token;
    this.socket = null;
    this.sessionId = null;
    this.currentStep = 0;
    this.stepContent = {};
  }
  
  connect() {
    this.socket = io('http://localhost:5000', {
      auth: { token: this.token },
      transports: ['websocket']
    });
    
    this.setupListeners();
  }
  
  setupListeners() {
    // Conexión
    this.socket.on('connect', () => {
      console.log('Conectado');
    });
    
    this.socket.on('connection_established', (data) => {
      this.sessionId = data.session_id;
      console.log('Sesión creada:', this.sessionId);
    });
    
    // Errores
    this.socket.on('error', (error) => {
      this.handleError(error);
    });
    
    // Streaming
    this.socket.on('waiting_phrase', (data) => {
      this.showLoading(data.message);
    });
    
    this.socket.on('explanation_start', (data) => {
      this.initExplanation(data);
    });
    
    this.socket.on('step_start', (data) => {
      this.currentStep = data.step;
      this.stepContent[data.step] = '';
      this.createStepUI(data);
    });
    
    this.socket.on('content_chunk', (data) => {
      this.stepContent[data.step] += data.chunk;
      this.updateStepContent(data.step, this.stepContent[data.step]);
    });
    
    this.socket.on('canvas_command', (data) => {
      this.executeCanvasCommand(data.step, data.command);
    });
    
    this.socket.on('step_complete', (data) => {
      this.markStepComplete(data.step);
    });
    
    this.socket.on('explanation_complete', (data) => {
      this.finishExplanation(data);
    });
  }
  
  askQuestion(question, context = {}) {
    this.socket.emit('ask_question', {
      token: this.token,
      question,
      context
    });
  }
  
  pauseExplanation() {
    this.socket.emit('pause_explanation', {
      token: this.token
    });
  }
  
  resumeExplanation() {
    this.socket.emit('resume_explanation', {
      token: this.token
    });
  }
  
  askFollowUp(question, relatedTo) {
    this.socket.emit('ask_follow_up_question', {
      question,
      related_to: relatedTo
    });
  }
  
  interrupt(clarificationQuestion, context) {
    this.socket.emit('interrupt_explanation', {
      clarification_question: clarificationQuestion,
      current_context: context
    });
  }
  
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
    }
  }
  
  // Métodos de UI (implementar según tu framework)
  showLoading(message) { /* ... */ }
  initExplanation(data) { /* ... */ }
  createStepUI(data) { /* ... */ }
  updateStepContent(step, content) { /* ... */ }
  executeCanvasCommand(step, command) { /* ... */ }
  markStepComplete(step) { /* ... */ }
  finishExplanation(data) { /* ... */ }
  handleError(error) { /* ... */ }
}

// Uso
const token = localStorage.getItem('supabase_token');
const guiaSocket = new GuiaIPNSocket(token);
guiaSocket.connect();

// Hacer pregunta
guiaSocket.askQuestion('¿Qué es la energía cinética?', {
  subject: 'fisica',
  difficulty: 'medium'
});
```

---

## 🔐 Autenticación en Socket.IO

### Conexión Inicial
```javascript
const socket = io('http://localhost:5000', {
  auth: {
    token: 'jwt_token_from_supabase'
  }
});
```

### En Cada Evento
```javascript
socket.emit('ask_question', {
  token: 'jwt_token', // Requerido en cada evento
  question: '...',
  context: {}
});
```

### Renovación de Token
```javascript
// Si el token expira durante la sesión:
socket.on('error', (error) => {
  if (error.code === 'AUTH_FAILED') {
    // Renovar token con Supabase
    const newToken = await supabase.auth.refreshSession();
    
    // Reconectar con nuevo token
    socket.disconnect();
    socket.auth.token = newToken;
    socket.connect();
  }
});
```

---

## 📊 Resumen de Eventos

### Cliente → Servidor
| Evento | Descripción | Requiere Auth |
|--------|-------------|---------------|
| `ask_question` | Hace una pregunta libre | ✅ |
| `pause_explanation` | Pausa streaming | ✅ |
| `resume_explanation` | Reanuda streaming | ✅ |
| `start_explanation` | Explica pregunta de examen | ❌ |
| `explanation_feedback` | Feedback de explicación | ❌ |
| `ask_follow_up_question` | Pregunta adicional | ❌ |
| `interrupt_explanation` | Interrupción/aclaración | ❌ |

### Servidor → Cliente
| Evento | Descripción | Cuándo |
|--------|-------------|--------|
| `connection_established` | Confirmación de conexión | Al conectar |
| `error` | Error general | Cualquier error |
| `waiting_phrase` | Mensaje de espera | Generando con IA |
| `explanation_start` | Inicio de explicación | Antes de steps |
| `step_start` | Inicio de paso | Por cada paso |
| `content_chunk` | Chunk de contenido | Durante paso |
| `canvas_command` | Comando de visualización | Durante paso |
| `step_complete` | Fin de paso | Después de paso |
| `explanation_complete` | Fin de explicación | Al terminar |
| `explanation_paused` | Confirmación de pausa | Al pausar |
| `streaming_resumed` | Confirmación de resume | Al reanudar |
| `follow_up_start` | Inicio de follow-up | Follow-up |
| `follow_up_complete` | Fin de follow-up | Follow-up |
| `follow_up_options` | Opciones post follow-up | Follow-up |
| `clarification_start` | Inicio de aclaración | Interrupción |
| `clarification_chunk` | Chunk de aclaración | Interrupción |
| `clarification_complete` | Fin de aclaración | Interrupción |
| `clarification_options` | Opciones post aclaración | Interrupción |
| `explanation_resumed` | Reanudación post interrupción | Resume |
| `feedback_recorded` | Confirmación de feedback | Feedback |
