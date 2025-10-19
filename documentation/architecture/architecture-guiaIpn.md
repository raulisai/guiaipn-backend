ARQUITECTURA BACKEND - SISTEMA DE APRENDIZAJE INMERSIVO
========================================================

1. STACK TECNOLÓGICO
--------------------
Frontend: Svelte + Socket.IO Client
Backend: Flask + Flask-SocketIO
Base de Datos: Supabase (PostgreSQL)
Cache: Redis
Auth: Supabase Auth (Google OAuth)
IA: OpenAI API
Transcripción: Web Speech API (MVP)

2. ESTRUCTURA DE ARCHIVOS
-------------------------
backend/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuraciones
│   ├── extensions.py        # Inicializar extensiones
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── decorators.py    # @require_auth
│   │   └── supabase.py      # Cliente Supabase
│   │
│   ├── socket_events/
│   │   ├── __init__.py
│   │   ├── connection.py    # connect/disconnect
│   │   ├── questions.py     # ask_question, interrupt
│   │   ├── voice.py         # voice_start, voice_complete
│   │   └── playback.py      # pause, resume
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── question_service.py    # Lógica de preguntas
│   │   ├── streaming_service.py   # Control de streaming
│   │   ├── ai_service.py          # OpenAI integration
│   │   ├── voice_service.py       # Transcripción
│   │   └── session_service.py     # Gestión de sesiones
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── answer_repository.py   # CRUD respuestas
│   │   ├── session_repository.py  # Redis operations
│   │   └── voice_repository.py    # Historial voz
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── answer.py        # Esquema respuestas
│   │   ├── session.py       # Esquema sesiones
│   │   └── voice.py         # Esquema interacciones voz
│   │
│   └── utils/
│       ├── __init__.py
│       ├── text_processing.py     # Normalizar, hash
│       ├── canvas_commands.py     # Generar comandos dibujo
│       ├── validators.py          # Validaciones
│       └── rate_limiter.py        # Control de rate
│
├── migrations/              # SQL migrations para Supabase
│   ├── 001_create_tables.sql
│   ├── 002_add_indexes.sql
│   └── 003_seed_data.sql
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
├── requirements.txt
├── .env.example
├── run.py                   # Entry point
└── README.md

3. FLUJO PRINCIPAL DEL SISTEMA
-------------------------------

[INICIO]
   |
   v
[Cliente Web] --WebSocket--> [Flask-SocketIO Server]
   |                                |
   v                                v
[Supabase Auth]              [Session Manager]
Google OAuth                  (Redis - TTL 30min)
   |                                |
   v                                v
[Usuario Autenticado] --------> [Event Handler]
                                    |
                    +---------------+---------------+
                    |                               |
                    v                               v
              [Pregunta Texto]               [Pregunta Voz]
                    |                               |
                    v                               v
            [Normalizar texto]              [Grabar audio]
            - Lowercase                     - Web Speech API
            - Quitar acentos                - Límite 60s
            - Trim espacios                      |
                    |                            v
                    v                      [Transcribir]
            [Generar SHA256]               - A texto español
                    |                            |
                    |                            v
                    +<---------------------------+
                    |
                    v
            [Buscar en DB]
            Supabase PostgreSQL
                    |
        +-----------+-----------+
        |                       |
        v                       v
    [EXISTE]                [NO EXISTE]
    (<200ms)                    |
        |                       v
        |                 [Mostrar "Pensando..."]
        |                       |
        |                       v
        |                 [Generar con OpenAI]
        |                 - Prompt estructurado
        |                 - Formato JSON
        |                 - Max 2000 tokens
        |                       |
        |                       v
        |                 [Guardar en DB]
        |                       |
        v                       v
        +----------->+<---------+
                     |
                     v
              [Iniciar Streaming]
                     |
                     v
              [Enviar metadata]
              {total_steps, duration}
                     |
                     v
         +----->[LOOP: Por cada paso]
         |           |
         |           v
         |      [step_start]
         |      - Título
         |      - Tipo contenido
         |           |
         |           v
         |      [Chunks de texto]
         |      - 50-100ms intervalo
         |      - Typewriter effect
         |           |
         |           v
         |      [Comandos canvas]
         |      - Figuras básicas
         |      - Animaciones
         |           |
         |           v
         |      ¿Interrupción?
         |       SI / NO
         |       |     |
         |       v     |
         |   [PAUSAR]  |
         |      |      |
         |      v      |
         |   [Procesar |
         |   pregunta] |
         |      |      |
         |      v      |
         |   [Mini     |
         |   respuesta]|
         |      |      |
         |      v      v
         |   [¿Continuar?]
         |    SI / NO
         |    |     |
         |    v     v
         |    |   [Nueva pregunta]
         |    |
         |    v
         +---[step_complete]
                     |
                     v
              ¿Más pasos?
               SI / NO
               |     |
               |     v
               |  [explanation_complete]
               |     |
               |     v
               |  [Solicitar feedback]
               |     |
               |     v
               |  [FIN]
               |
               v
            [Siguiente paso]

4. ESQUEMAS DE BASE DE DATOS (SUPABASE)
----------------------------------------

-- Tabla: predefined_answers
CREATE TABLE predefined_answers (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    question_hash VARCHAR(64) UNIQUE NOT NULL,
    question_original TEXT NOT NULL,
    category VARCHAR(50),
    difficulty VARCHAR(20) CHECK (difficulty IN ('easy', 'medium', 'hard')),
    steps JSONB NOT NULL,
    total_duration INTEGER DEFAULT 0,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(20) DEFAULT 'manual',
    feedback_score FLOAT DEFAULT 0.0
);

-- Índices
CREATE INDEX idx_question_hash ON predefined_answers(question_hash);
CREATE INDEX idx_category ON predefined_answers(category, difficulty);
CREATE INDEX idx_usage ON predefined_answers(usage_count DESC);

-- Tabla: voice_interactions
CREATE TABLE voice_interactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    session_id VARCHAR(36) NOT NULL,
    audio_url TEXT,
    transcription TEXT NOT NULL,
    transcription_method VARCHAR(20),
    confidence_score FLOAT,
    processing_time_ms INTEGER,
    was_confirmed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla: interaction_history
CREATE TABLE interaction_history (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    session_id VARCHAR(36) NOT NULL,
    question TEXT NOT NULL,
    answer_source VARCHAR(20),
    response_time_ms INTEGER,
    was_interrupted BOOLEAN DEFAULT FALSE,
    interruption_count INTEGER DEFAULT 0,
    feedback_rating INTEGER CHECK (feedback_rating >= 1 AND feedback_rating <= 5),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS Policies
ALTER TABLE predefined_answers ENABLE ROW LEVEL SECURITY;
ALTER TABLE voice_interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE interaction_history ENABLE ROW LEVEL SECURITY;

-- Políticas de seguridad
CREATE POLICY "Answers are viewable by everyone" 
    ON predefined_answers FOR SELECT 
    USING (true);

CREATE POLICY "Voice interactions belong to users" 
    ON voice_interactions FOR ALL 
    USING (auth.uid() = user_id);

CREATE POLICY "History belongs to users" 
    ON interaction_history FOR ALL 
    USING (auth.uid() = user_id);

5. CONFIGURACIÓN REDIS
----------------------

# Estructura de keys en Redis

# Sesiones activas
session:{session_id} = {
    "user_id": "uuid",
    "connection_id": "socket_id",
    "current_question": "hash",
    "current_step": 0,
    "pause_position": 0,
    "is_paused": false,
    "is_streaming": false,
    "conversation_context": {},
    "created_at": "timestamp",
    "last_activity": "timestamp"
}
TTL: 1800 segundos (30 minutos)

# Cache de respuestas
answer_cache:{question_hash} = {
    "steps": [...],
    "total_duration": 120,
    "cached_at": "timestamp"
}
TTL: 86400 segundos (24 horas)

# Estado de audio/voz
voice_state:{session_id} = {
    "is_recording": false,
    "start_time": "timestamp",
    "chunks_received": 0
}
TTL: 300 segundos (5 minutos)

# Rate limiting
rate_limit:{user_id}:questions = count
TTL: 60 segundos
MAX: 10 preguntas por minuto

6. EVENTOS SOCKET.IO DETALLADOS
--------------------------------

=== CLIENTE -> SERVIDOR ===

1. connect
   payload: {
       auth: {
           token: "supabase_jwt_token"
       }
   }
   proceso:
   - Validar token con Supabase
   - Crear/recuperar session_id
   - Guardar en Redis
   - Emit: connection_established

2. ask_question
   payload: {
       question: "texto de la pregunta",
       context: {} // opcional
   }
   proceso:
   - Validar pregunta no vacía
   - Check rate limit
   - Normalizar y generar hash
   - Buscar en DB
   - Iniciar streaming

3. voice_start
   payload: {
       session_id: "uuid"
   }
   proceso:
   - Pausar streaming actual
   - Actualizar estado en Redis
   - Preparar para recibir audio
   - Emit: voice_recording_started

4. voice_complete
   payload: {
       audio_data: "base64_audio",
       duration: 5000 // ms
   }
   proceso:
   - Transcribir con Web Speech
   - Mostrar transcripción
   - Esperar confirmación

5. pause_explanation
   payload: {
       current_step: 3,
       position_in_step: 150
   }
   proceso:
   - Detener streaming
   - Guardar posición
   - Actualizar Redis
   - Emit: explanation_paused

6. resume_explanation
   payload: {}
   proceso:
   - Recuperar posición
   - Continuar streaming
   - Emit: explanation_resumed

=== SERVIDOR -> CLIENTE ===

1. connection_established
   payload: {
       session_id: "uuid",
       user_info: {
           email: "user@gmail.com"
       }
   }

2. waiting_phrase
   payload: {
       phrase: "Déjame buscar eso...",
       category: "searching",
       estimated_time: 2000
   }

3. explanation_start
   payload: {
       total_steps: 5,
       estimated_duration: 180,
       question_hash: "abc123"
   }

4. step_start
   payload: {
       step_number: 1,
       title: "Introducción al tema",
       content_type: "text",
       has_visual: false
   }

5. content_chunk
   payload: {
       step_number: 1,
       chunk: "Este es el siguiente fragmento...",
       position: 150,
       is_final: false
   }

6. canvas_command
   payload: {
       step_number: 2,
       command: {
           type: "rectangle",
           x: 100,
           y: 100,
           width: 200,
           height: 150,
           color: "#3498db"
       }
   }

7. step_complete
   payload: {
       step_number: 1,
       duration_actual: 15000
   }

8. explanation_complete
   payload: {
       total_duration: 180000,
       steps_completed: 5
   }

9. voice_transcription_result
   payload: {
       transcription: "¿Qué significa esto?",
       confidence: 0.95,
       requires_confirmation: true
   }

10. error
    payload: {
        code: "RATE_LIMIT_EXCEEDED",
        message: "Demasiadas preguntas",
        retry_after: 30
    }

7. SERVICIOS PRINCIPALES
------------------------

=== QuestionService ===
class QuestionService:
    def process_question(question: str) -> dict:
        # 1. Validar
        # 2. Normalizar
        # 3. Generar hash
        # 4. Buscar en DB
        # 5. Si no existe, generar con IA
        # 6. Retornar respuesta estructurada

    def normalize_text(text: str) -> str:
        # Lowercase
        # Quitar acentos
        # Trim espacios
        # Remover puntuación extra

    def generate_hash(text: str) -> str:
        # SHA256 del texto normalizado

=== StreamingService ===
class StreamingService:
    def start_streaming(answer: dict, session_id: str):
        # 1. Enviar metadata
        # 2. Por cada paso:
        #    - Enviar step_start
        #    - Chunks de texto
        #    - Comandos canvas
        #    - step_complete
        # 3. explanation_complete

    def pause_streaming(session_id: str, position: dict):
        # Guardar estado actual
        # Detener envío de chunks

    def resume_streaming(session_id: str):
        # Recuperar estado
        # Continuar desde posición

=== AIService ===
class AIService:
    def generate_answer(question: str, context: dict) -> dict:
        # 1. Construir prompt
        # 2. Llamar OpenAI API
        # 3. Parsear respuesta JSON
        # 4. Validar estructura
        # 5. Retornar steps formateados

    def build_prompt(question: str) -> str:
        # System prompt + ejemplos
        # Instrucciones de formato
        # Contexto si existe

=== VoiceService ===
class VoiceService:
    def transcribe_audio(audio_data: bytes) -> dict:
        # 1. Decodificar base64
        # 2. Usar Web Speech API
        # 3. Retornar transcripción
        # 4. Incluir confidence score

=== SessionService ===
class SessionService:
    def create_session(user_id: str) -> str:
        # Generar UUID
        # Guardar en Redis
        # Retornar session_id

    def get_session(session_id: str) -> dict:
        # Buscar en Redis
        # Actualizar last_activity
        # Retornar datos

    def update_session(session_id: str, data: dict):
        # Actualizar campos
        # Renovar TTL

8. FLUJO DE AUTENTICACIÓN
-------------------------

[Usuario] --> [Login con Google] --> [Supabase Auth]
                                           |
                                           v
                                    [JWT Token]
                                           |
                                           v
[Frontend almacena token] --> [Envía en Socket.IO connect]
                                           |
                                           v
                              [Backend valida con Supabase]
                                           |
                                    +------+------+
                                    |             |
                                    v             v
                               [Válido]      [Inválido]
                                    |             |
                                    v             v
                          [Crear sesión]   [Rechazar conexión]
                                    |
                                    v
                            [Usuario conectado]

9. MANEJO DE ERRORES
--------------------

try:
    # Operación principal
except ValidationError:
    emit('error', {
        'code': 'INVALID_INPUT',
        'message': 'Pregunta inválida'
    })
except RateLimitError:
    emit('error', {
        'code': 'RATE_LIMIT',
        'message': 'Demasiadas preguntas',
        'retry_after': 60
    })
except OpenAIError:
    # Fallback a respuesta genérica
    emit('waiting_phrase', {
        'phrase': 'Disculpa, hay un problema temporal'
    })
except Exception as e:
    # Log error
    # Emit generic error
    # No exponer detalles internos

10. VARIABLES DE ENTORNO
------------------------

# .env
FLASK_ENV=development
SECRET_KEY=your-secret-key
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-...
CORS_ORIGINS=http://localhost:5173
MAX_CONNECTIONS_PER_IP=5
RATE_LIMIT_QUESTIONS=10
RATE_LIMIT_WINDOW=60