# 📊 Diagramas de Flujo Detallados

## 1. Flujo de Autenticación Completo

```
┌─────────────┐
│   Usuario   │
└──────┬──────┘
       │
       │ 1. Click "Iniciar con Google"
       ▼
┌─────────────┐
│  Frontend   │
└──────┬──────┘
       │
       │ 2. signInWithOAuth()
       ▼
┌─────────────┐
│  Supabase   │
│    Auth     │
└──────┬──────┘
       │
       │ 3. Redirige a Google OAuth
       ▼
┌─────────────┐
│   Google    │
│    OAuth    │
└──────┬──────┘
       │
       │ 4. Usuario autoriza
       ▼
┌─────────────┐
│  Supabase   │
│    Auth     │
└──────┬──────┘
       │
       │ 5. Retorna JWT token
       ▼
┌─────────────┐
│  Frontend   │
│  /callback  │
└──────┬──────┘
       │
       │ 6. POST /auth/initialize
       │    { token: "jwt..." }
       ▼
┌─────────────┐
│   Backend   │
│  GuiaIPN    │
└──────┬──────┘
       │
       ├─→ 7a. Verifica token con Supabase
       │
       ├─→ 7b. Crea perfil en tabla 'profiles'
       │
       ├─→ 7c. Inicializa 'user_progress' (8 materias)
       │
       │ 8. Retorna perfil creado
       ▼
┌─────────────┐
│  Frontend   │
└──────┬──────┘
       │
       │ 9. Guarda token + redirige a /dashboard
       ▼
┌─────────────┐
│  Dashboard  │
└─────────────┘
```

---

## 2. Flujo de Pregunta con Streaming (Detallado)

```
┌──────────┐                ┌──────────┐                ┌──────────┐                ┌──────────┐                ┌──────────┐
│ Frontend │                │  Backend │                │   Redis  │                │ Supabase │                │  OpenAI  │
└────┬─────┘                └────┬─────┘                └────┬─────┘                └────┬─────┘                └────┬─────┘
     │                           │                           │                           │                           │
     │ 1. socket.emit(           │                           │                           │                           │
     │    'ask_question',        │                           │                           │                           │
     │    {token, question})     │                           │                           │                           │
     ├──────────────────────────→│                           │                           │                           │
     │                           │                           │                           │                           │
     │                           │ 2. Verificar token        │                           │                           │
     │                           ├───────────────────────────────────────────────────────→│                           │
     │                           │←──────────────────────────────────────────────────────┤                           │
     │                           │                           │                           │                           │
     │                           │ 3. Obtener/crear sesión   │                           │                           │
     │                           ├──────────────────────────→│                           │                           │
     │                           │←──────────────────────────┤                           │                           │
     │                           │   session_id              │                           │                           │
     │                           │                           │                           │                           │
     │                           │ 4. Validar pregunta       │                           │                           │
     │                           │    (5-1000 chars)         │                           │                           │
     │                           │                           │                           │                           │
     │                           │ 5. Normalizar texto       │                           │                           │
     │                           │    (lowercase, trim,      │                           │                           │
     │                           │     remove accents)       │                           │                           │
     │                           │                           │                           │                           │
     │                           │ 6. Generar hash SHA256    │                           │                           │
     │                           │                           │                           │                           │
     │                           │ 7. Buscar en cache        │                           │                           │
     │                           ├───────────────────────────────────────────────────────→│                           │
     │                           │   SELECT * FROM           │                           │                           │
     │                           │   ai_answers WHERE        │                           │                           │
     │                           │   question_hash = ?       │                           │                           │
     │                           │←──────────────────────────────────────────────────────┤                           │
     │                           │                           │                           │                           │
     │                           │ 8a. Si NO existe:         │                           │                           │
     │                           │                           │                           │                           │
     │ 9. waiting_phrase         │                           │                           │                           │
     │←──────────────────────────┤                           │                           │                           │
     │ "Analizando tu pregunta"  │                           │                           │                           │
     │                           │                           │                           │                           │
     │                           │ 10. Generar con OpenAI    │                           │                           │
     │                           ├───────────────────────────────────────────────────────────────────────────────────→│
     │                           │   POST /chat/completions  │                           │                           │
     │                           │   {model: "gpt-4",        │                           │                           │
     │                           │    messages: [...]}       │                           │                           │
     │                           │←──────────────────────────────────────────────────────────────────────────────────┤
     │                           │   JSON response           │                           │                           │
     │                           │                           │                           │                           │
     │                           │ 11. Parsear JSON          │                           │                           │
     │                           │     Validar estructura    │                           │                           │
     │                           │                           │                           │                           │
     │                           │ 12. Guardar en DB         │                           │                           │
     │                           ├───────────────────────────────────────────────────────→│                           │
     │                           │   INSERT INTO ai_answers  │                           │                           │
     │                           │←──────────────────────────────────────────────────────┤                           │
     │                           │                           │                           │                           │
     │                           │ 8b. Si existe:            │                           │                           │
     │                           │     Incrementar uso       │                           │                           │
     │                           ├───────────────────────────────────────────────────────→│                           │
     │                           │   UPDATE ai_answers       │                           │                           │
     │                           │   SET times_used += 1     │                           │                           │
     │                           │                           │                           │                           │
     │                           │ 13. Actualizar sesión     │                           │                           │
     │                           ├──────────────────────────→│                           │                           │
     │                           │   HSET session:uuid       │                           │                           │
     │                           │   current_question hash   │                           │                           │
     │                           │   is_streaming true       │                           │                           │
     │                           │                           │                           │                           │
     │ 14. explanation_start     │                           │                           │                           │
     │←──────────────────────────┤                           │                           │                           │
     │ {total_steps: 4,          │                           │                           │                           │
     │  estimated_duration: 120} │                           │                           │                           │
     │                           │                           │                           │                           │
     │                           │ 15. Iniciar streaming     │                           │                           │
     │                           │     (loop por cada paso)  │                           │                           │
     │                           │                           │                           │                           │
     │ 16. step_start            │                           │                           │                           │
     │←──────────────────────────┤                           │                           │                           │
     │ {step: 0,                 │                           │                           │                           │
     │  title: "Definición",     │                           │                           │                           │
     │  type: "text"}            │                           │                           │                           │
     │                           │                           │                           │                           │
     │                           │ 17. Dividir contenido     │                           │                           │
     │                           │     en chunks de 50 chars │                           │                           │
     │                           │                           │                           │                           │
     │ 18. content_chunk (x N)   │                           │                           │                           │
     │←──────────────────────────┤                           │                           │                           │
     │ {step: 0,                 │                           │                           │                           │
     │  chunk: "La energía...",  │                           │                           │                           │
     │  position: 0,             │                           │                           │                           │
     │  is_final: false}         │                           │                           │                           │
     │                           │ (delay 50ms)              │                           │                           │
     │←──────────────────────────┤                           │                           │                           │
     │ {chunk: "cinética es..."}│                           │                           │                           │
     │                           │                           │                           │                           │
     │                           │ 19. Si hay canvas_commands│                           │                           │
     │ 20. canvas_command        │                           │                           │                           │
     │←──────────────────────────┤                           │                           │                           │
     │ {step: 0,                 │                           │                           │                           │
     │  command: {type: "draw_   │                           │                           │                           │
     │  axis", x: 50, y: 200}}   │                           │                           │                           │
     │                           │                           │                           │                           │
     │ 21. step_complete         │                           │                           │                           │
     │←──────────────────────────┤                           │                           │                           │
     │ {step: 0}                 │                           │                           │                           │
     │                           │                           │                           │                           │
     │ [Repetir 16-21 para       │                           │                           │                           │
     │  cada paso restante]      │                           │                           │                           │
     │                           │                           │                           │                           │
     │ 22. explanation_complete  │                           │                           │                           │
     │←──────────────────────────┤                           │                           │                           │
     │ {total_duration: 120,     │                           │                           │                           │
     │  steps_completed: 4}      │                           │                           │                           │
     │                           │                           │                           │                           │
     │                           │ 23. Actualizar sesión     │                           │                           │
     │                           ├──────────────────────────→│                           │                           │
     │                           │   HSET session:uuid       │                           │                           │
     │                           │   is_streaming false      │                           │                           │
     │                           │   EXPIRE session:uuid     │                           │                           │
     │                           │   1800                    │                           │                           │
```

---

## 3. Flujo de Pause/Resume

```
┌──────────┐                ┌──────────┐                ┌──────────┐
│ Frontend │                │  Backend │                │   Redis  │
└────┬─────┘                └────┬─────┘                └────┬─────┘
     │                           │                           │
     │ [Streaming en progreso]   │                           │
     │                           │                           │
     │ 1. Usuario click "Pausar" │                           │
     │                           │                           │
     │ 2. socket.emit(           │                           │
     │    'pause_explanation')   │                           │
     ├──────────────────────────→│                           │
     │                           │                           │
     │                           │ 3. Obtener sesión         │
     │                           ├──────────────────────────→│
     │                           │←──────────────────────────┤
     │                           │                           │
     │                           │ 4. Actualizar estado      │
     │                           ├──────────────────────────→│
     │                           │   HSET session:uuid       │
     │                           │   is_paused true          │
     │                           │   pause_position 150      │
     │                           │   is_streaming false      │
     │                           │                           │
     │                           │ 5. Detener loop streaming │
     │                           │                           │
     │ 6. explanation_paused     │                           │
     │←──────────────────────────┤                           │
     │ {message: "Pausado",      │                           │
     │  session_id: "uuid"}      │                           │
     │                           │                           │
     │ [Usuario espera...]       │                           │
     │                           │                           │
     │ 7. Usuario click "Reanudar"│                          │
     │                           │                           │
     │ 8. socket.emit(           │                           │
     │    'resume_explanation')  │                           │
     ├──────────────────────────→│                           │
     │                           │                           │
     │                           │ 9. Obtener sesión         │
     │                           ├──────────────────────────→│
     │                           │←──────────────────────────┤
     │                           │   {pause_position: 150,   │
     │                           │    current_step: 2}       │
     │                           │                           │
     │                           │ 10. Actualizar estado     │
     │                           ├──────────────────────────→│
     │                           │   HSET session:uuid       │
     │                           │   is_paused false         │
     │                           │   is_streaming true       │
     │                           │                           │
     │ 11. streaming_resumed     │                           │
     │←──────────────────────────┤                           │
     │ {step: 2,                 │                           │
     │  position: 150}           │                           │
     │                           │                           │
     │                           │ 12. Continuar desde       │
     │                           │     posición 150          │
     │                           │                           │
     │ 13. content_chunk         │                           │
     │←──────────────────────────┤                           │
     │ (continúa streaming)      │                           │
```

---

## 4. Flujo de Pregunta de Examen

```
┌──────────┐                ┌──────────┐                ┌──────────┐
│ Frontend │                │  Backend │                │ Supabase │
└────┬─────┘                └────┬─────┘                └────┬─────┘
     │                           │                           │
     │ 1. GET /questions/random  │                           │
     │    ?subject=matematicas   │                           │
     ├──────────────────────────→│                           │
     │                           │                           │
     │                           │ 2. SELECT random pregunta │
     │                           ├──────────────────────────→│
     │                           │←──────────────────────────┤
     │                           │                           │
     │ 3. Retorna pregunta       │                           │
     │←──────────────────────────┤                           │
     │ {id, question_text,       │                           │
     │  option_a, option_b, ...} │                           │
     │                           │                           │
     │ 4. Usuario selecciona "a" │                           │
     │                           │                           │
     │ 5. POST /questions/{id}/  │                           │
     │    answer                 │                           │
     │    {user_answer: "a"}     │                           │
     ├──────────────────────────→│                           │
     │                           │                           │
     │                           │ 6. Validar respuesta      │
     │                           ├──────────────────────────→│
     │                           │←──────────────────────────┤
     │                           │                           │
     │ 7. Retorna resultado      │                           │
     │←──────────────────────────┤                           │
     │ {is_correct: true,        │                           │
     │  correct_answer: "a"}     │                           │
     │                           │                           │
     │ 8. Usuario click          │                           │
     │    "Ver explicación"      │                           │
     │                           │                           │
     │ 9. socket.emit(           │                           │
     │    'start_explanation',   │                           │
     │    {question_id,          │                           │
     │     user_answer})         │                           │
     ├──────────────────────────→│                           │
     │                           │                           │
     │                           │ 10. Buscar explicación    │
     │                           ├──────────────────────────→│
     │                           │   SELECT * FROM           │
     │                           │   exam_explanations       │
     │                           │   WHERE question_id = ?   │
     │                           │←──────────────────────────┤
     │                           │                           │
     │                           │ 11a. Si NO existe:        │
     │                           │      Generar con IA       │
     │                           │      Guardar en DB        │
     │                           │                           │
     │ 12. waiting_phrase        │                           │
     │←──────────────────────────┤                           │
     │                           │                           │
     │ 13. explanation_start     │                           │
     │←──────────────────────────┤                           │
     │                           │                           │
     │ [Streaming normal...]     │                           │
     │                           │                           │
     │ 14. explanation_complete  │                           │
     │←──────────────────────────┤                           │
     │                           │                           │
     │ 15. Mostrar botones:      │                           │
     │     - ¿Fue útil? 👍👎     │                           │
     │     - Hacer pregunta      │                           │
     │       adicional           │                           │
```

---

## 5. Flujo de Follow-up Question

```
┌──────────┐                ┌──────────┐                ┌──────────┐
│ Frontend │                │  Backend │                │ Supabase │
└────┬─────┘                └────┬─────┘                └────┬─────┘
     │                           │                           │
     │ [Después de explicación]  │                           │
     │                           │                           │
     │ 1. Usuario escribe:       │                           │
     │    "¿Y en movimiento      │                           │
     │     circular?"            │                           │
     │                           │                           │
     │ 2. socket.emit(           │                           │
     │    'ask_follow_up_        │                           │
     │    question',             │                           │
     │    {question: "...",      │                           │
     │     related_to: "uuid"})  │                           │
     ├──────────────────────────→│                           │
     │                           │                           │
     │                           │ 3. Obtener pregunta       │
     │                           │    original               │
     │                           ├──────────────────────────→│
     │                           │←──────────────────────────┤
     │                           │                           │
     │                           │ 4. Normalizar + hash      │
     │                           │                           │
     │                           │ 5. Buscar en cache        │
     │                           ├──────────────────────────→│
     │                           │←──────────────────────────┤
     │                           │                           │
     │                           │ 6. Si NO existe:          │
     │                           │    Generar con IA         │
     │                           │    (incluye contexto      │
     │                           │     de pregunta original) │
     │                           │                           │
     │ 7. waiting_phrase         │                           │
     │←──────────────────────────┤                           │
     │                           │                           │
     │                           │ 8. Guardar respuesta      │
     │                           ├──────────────────────────→│
     │                           │   INSERT INTO ai_answers  │
     │                           │   related_question_id =   │
     │                           │   "uuid_original"         │
     │                           │                           │
     │ 9. follow_up_start        │                           │
     │←──────────────────────────┤                           │
     │ {answer_id: "uuid",       │                           │
     │  is_follow_up: true}      │                           │
     │                           │                           │
     │ [Streaming normal...]     │                           │
     │                           │                           │
     │ 10. follow_up_complete    │                           │
     │←──────────────────────────┤                           │
     │                           │                           │
     │ 11. follow_up_options     │                           │
     │←──────────────────────────┤                           │
     │ {options: [               │                           │
     │   'more_questions',       │                           │
     │   'finish']}              │                           │
```

---

## 6. Flujo de Interrupción/Aclaración

```
┌──────────┐                ┌──────────┐
│ Frontend │                │  Backend │
└────┬─────┘                └────┬─────┘
     │                           │
     │ [Streaming en progreso]   │
     │                           │
     │ 1. Usuario click          │
     │    "No entiendo X"        │
     │                           │
     │ 2. socket.emit(           │
     │    'interrupt_            │
     │    explanation',          │
     │    {clarification_        │
     │     question: "...",      │
     │     current_context})     │
     ├──────────────────────────→│
     │                           │
     │                           │ 3. Pausar streaming       │
     │                           │    principal              │
     │                           │                           │
     │ 4. clarification_start    │                           │
     │←──────────────────────────┤                           │
     │ {is_brief: true,          │                           │
     │  estimated_duration: 15}  │                           │
     │                           │                           │
     │                           │ 5. Generar aclaración     │
     │                           │    breve con IA           │
     │                           │                           │
     │ 6. clarification_chunk    │                           │
     │←──────────────────────────┤                           │
     │ (streaming rápido)        │                           │
     │                           │                           │
     │ 7. clarification_complete │                           │
     │←──────────────────────────┤                           │
     │                           │                           │
     │ 8. clarification_options  │                           │
     │←──────────────────────────┤                           │
     │ {options: [               │                           │
     │   'continue',             │                           │
     │   'new_question']}        │                           │
     │                           │                           │
     │ 9. Usuario click          │                           │
     │    "Continuar"            │                           │
     │                           │                           │
     │ 10. socket.emit(          │                           │
     │     'resume_explanation') │                           │
     ├──────────────────────────→│                           │
     │                           │                           │
     │ 11. explanation_resumed   │                           │
     │←──────────────────────────┤                           │
     │                           │                           │
     │ [Continúa streaming       │                           │
     │  principal]               │                           │
```

---

## 7. Gestión de Sesiones Redis

```
┌──────────┐                ┌──────────┐                ┌──────────┐
│  Socket  │                │  Session │                │   Redis  │
│  Event   │                │  Service │                │          │
└────┬─────┘                └────┬─────┘                └────┬─────┘
     │                           │                           │
     │ connect                   │                           │
     ├──────────────────────────→│                           │
     │                           │ create_session()          │
     │                           ├──────────────────────────→│
     │                           │   HSET session:uuid       │
     │                           │   user_id, connection_id  │
     │                           │   EXPIRE session:uuid     │
     │                           │   1800                    │
     │                           │←──────────────────────────┤
     │                           │   session_id              │
     │←──────────────────────────┤                           │
     │ connection_established    │                           │
     │                           │                           │
     │ [Actividad del usuario]   │                           │
     │                           │                           │
     │ ask_question              │                           │
     ├──────────────────────────→│                           │
     │                           │ update_session()          │
     │                           ├──────────────────────────→│
     │                           │   HSET session:uuid       │
     │                           │   current_question hash   │
     │                           │   last_activity now       │
     │                           │   EXPIRE session:uuid     │
     │                           │   1800 (renovar TTL)      │
     │                           │                           │
     │ [30 minutos sin actividad]│                           │
     │                           │                           │
     │                           │                           │ TTL expira
     │                           │                           │ Redis elimina
     │                           │                           │ automáticamente
     │                           │                           │
     │ disconnect                │                           │
     ├──────────────────────────→│                           │
     │                           │ end_session()             │
     │                           ├──────────────────────────→│
     │                           │   DEL session:uuid        │
     │                           │←──────────────────────────┤
```

---

## 8. Cache de Respuestas IA

```
┌──────────┐                ┌──────────┐                ┌──────────┐
│  Pregunta│                │  Backend │                │ Supabase │
│  Usuario │                │          │                │ ai_answers│
└────┬─────┘                └────┬─────┘                └────┬─────┘
     │                           │                           │
     │ "¿Qué es la energía       │                           │
     │  cinética?"               │                           │
     ├──────────────────────────→│                           │
     │                           │                           │
     │                           │ 1. Normalizar:            │
     │                           │    "que es la energia     │
     │                           │     cinetica"             │
     │                           │                           │
     │                           │ 2. Hash SHA256:           │
     │                           │    "a1b2c3d4..."          │
     │                           │                           │
     │                           │ 3. Buscar en DB           │
     │                           ├──────────────────────────→│
     │                           │   SELECT * FROM           │
     │                           │   ai_answers WHERE        │
     │                           │   question_hash =         │
     │                           │   'a1b2c3d4...'           │
     │                           │←──────────────────────────┤
     │                           │                           │
     │                           │ 4a. Si existe:            │
     │                           │     - Incrementar uso     │
     │                           │     - Retornar respuesta  │
     │                           │                           │
     │                           │ 4b. Si NO existe:         │
     │                           │     - Generar con IA      │
     │                           │     - Guardar con hash    │
     │                           │     - Retornar respuesta  │
     │                           │                           │
     │ [Otro usuario hace        │                           │
     │  misma pregunta]          │                           │
     │                           │                           │
     │ "Que es la Energía        │                           │
     │  CINETICA?"               │                           │
     ├──────────────────────────→│                           │
     │                           │                           │
     │                           │ Normalizar → mismo hash   │
     │                           │ "a1b2c3d4..."             │
     │                           │                           │
     │                           │ Buscar → ENCONTRADO       │
     │                           ├──────────────────────────→│
     │                           │←──────────────────────────┤
     │                           │                           │
     │ Respuesta instantánea     │                           │
     │ (sin llamar a OpenAI)     │                           │
     │←──────────────────────────┤                           │
```

---

## Leyenda de Símbolos

```
│   Flujo vertical
├─→ Acción/llamada
←─┤ Respuesta/retorno
▼   Continúa hacia abajo
[...] Comentario/nota
```
