ARQUITECTURA BACKEND - SISTEMA DE APRENDIZAJE INMERSIVO
========================================================

1. STACK TECNOLÓGICO
--------------------
Frontend: Svelte + Socket.IO Client
Backend: Flask + Flask-SocketIO
Base de Datos: Supabase (PostgreSQL)
Documentacion: Swagger
Cache: Redis
Auth: Supabase Auth (Google OAuth)
IA: OpenAI API
Transcripción: Web Speech API (MVP)

2. ESTRUCTURA DE ARCHIVOS
-------------------------
backend/
├── app/
│   ├── __init__.py              # app factory (Flask + SocketIO)
│   ├── config.py
│   ├── extensions.py            # db, redis, socketio, swagger
│   │
│   ├── api/                     # HTTP API (Blueprints = controllers)
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth_routes.py       # /api/v1/auth
│   │   │   ├── question_routes.py   # /api/v1/questions
│   │   │   └── session_routes.py
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── decorators.py    # @require_auth
│   │   └── supabase.py      # Cliente Supabase
│   │
│   ├── socket_events/    # SocketIO handlers (thin controllers)
│   │   ├── __init__.py
│   │   ├── connection.py    # connect/disconnect
│   │   ├── questions.py     # ask_question, interrupt
│   │   ├── voice.py         # voice_start, voice_complete
│   │   └── playback.py      # pause, resume
│   │
│   ├── controllers/             # opcional: lógica HTTP+Socket común
│   │   ├── __init__.py
│   │   └── streaming_controller.py
│   │
│   ├── services/                # lógica de negocio
│   │   ├── __init__.py
│   │   ├── question_service.py
│   │   ├── ai_service.py
│   │   ├── streaming_service.py
│   │   ├── voice_service.py
│   │   └── session_service.py
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── question_repo.py
│   │   ├── ai_answers_repo.py
│   │   └── session_repo.py      # Redis ops
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
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── .env
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
├── .vscode/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run.py
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

-- Habilitar extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- Para búsquedas de texto
CREATE EXTENSION IF NOT EXISTS "unaccent"; -- Para normalizar texto

-- =========================================
-- 2. TABLAS CORE DEL SISTEMA
-- =========================================

-- Perfiles de usuario (extiende auth.users de Supabase)
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE,
    full_name TEXT,
    avatar_url TEXT,
    
    -- Plan y créditos
    plan_type TEXT DEFAULT 'free' CHECK (plan_type IN ('free', 'basic', 'premium', 'pro')),
    credits_remaining INTEGER DEFAULT 10,
    credits_total INTEGER DEFAULT 10,
    daily_limit INTEGER DEFAULT 5,
    daily_used INTEGER DEFAULT 0,
    last_reset_date DATE DEFAULT CURRENT_DATE,
    
    -- Configuración
    preferred_language TEXT DEFAULT 'es',
    learning_level TEXT DEFAULT 'medium',
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Banco de preguntas del examen
CREATE TABLE questions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    
    -- Identificación
    code TEXT UNIQUE NOT NULL, -- ej: "2024Algebra14"
    subject TEXT NOT NULL, -- algebra, calculo, fisica, etc
    topic TEXT,
    difficulty TEXT DEFAULT 'medium' CHECK (difficulty IN ('easy', 'medium', 'hard')),
    
    -- Contenido
    question TEXT NOT NULL,
    options JSONB NOT NULL, -- {a: "...", b: "...", c: "...", d: "..."}
    correct_answer TEXT NOT NULL,
    explanation TEXT,
    
    -- Configuración LaTeX
    use_latex BOOLEAN DEFAULT FALSE,
    
    -- Estadísticas
    times_seen INTEGER DEFAULT 0,
    times_correct INTEGER DEFAULT 0,
    exam_probability NUMERIC(3,2) DEFAULT 0.50, -- 0.00 a 1.00
    
    -- Metadata
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Respuestas IA precalculadas
CREATE TABLE ai_answers (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    question_hash TEXT UNIQUE NOT NULL, -- SHA256 de la pregunta normalizada
    question_text TEXT NOT NULL,
    
    -- Respuesta estructurada
    answer_steps JSONB NOT NULL, -- Array de pasos de explicación
    total_duration INTEGER DEFAULT 60, -- segundos estimados
    
    -- Estadísticas
    usage_count INTEGER DEFAULT 0,
    helpful_votes INTEGER DEFAULT 0,
    total_votes INTEGER DEFAULT 0,
    
    -- Metadata
    generated_by TEXT DEFAULT 'manual', -- manual, gpt-3.5, gpt-4
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Historial de interacciones
CREATE TABLE interactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    session_id TEXT,
    
    -- Pregunta y respuesta
    question_text TEXT NOT NULL,
    question_type TEXT DEFAULT 'text', -- text, voice, exam
    answer_id UUID REFERENCES ai_answers(id),
    question_id UUID REFERENCES questions(id),
    
    -- Métricas
    response_time_ms INTEGER,
    credits_used INTEGER DEFAULT 1,
    completed BOOLEAN DEFAULT TRUE,
    
    -- Feedback
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    understood BOOLEAN,
    seen_in_exam BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sesiones de estudio
CREATE TABLE study_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Información de sesión
    session_type TEXT DEFAULT 'practice', -- practice, exam, review
    status TEXT DEFAULT 'active', -- active, completed, abandoned
    
    -- Estadísticas
    questions_asked INTEGER DEFAULT 0,
    questions_answered INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    total_duration_seconds INTEGER DEFAULT 0,
    
    -- Timestamps
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Progreso del usuario
CREATE TABLE user_progress (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    subject TEXT NOT NULL,
    
    -- Métricas
    total_practiced INTEGER DEFAULT 0,
    total_correct INTEGER DEFAULT 0,
    mastery_level NUMERIC(3,2) DEFAULT 0.00, -- 0.00 a 1.00
    streak_days INTEGER DEFAULT 0,
    
    -- Timestamps
    last_practice_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id, subject)
);

-- Uso de créditos
CREATE TABLE credit_usage (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Detalle del uso
    action_type TEXT NOT NULL, -- ai_question, voice, premium_feature
    credits_used INTEGER NOT NULL,
    credits_before INTEGER NOT NULL,
    credits_after INTEGER NOT NULL,
    
    -- Contexto
    interaction_id UUID REFERENCES interactions(id),
    details JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Planes de suscripción
CREATE TABLE subscription_plans (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    
    -- Límites
    monthly_credits INTEGER NOT NULL,
    daily_limit INTEGER NOT NULL,
    
    -- Features
    features JSONB DEFAULT '{}'::jsonb,
    
    -- Precio
    price_monthly NUMERIC(10,2) DEFAULT 0,
    price_yearly NUMERIC(10,2) DEFAULT 0,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Suscripciones de usuarios
CREATE TABLE user_subscriptions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES subscription_plans(id),
    
    -- Estado
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'expired', 'trial')),
    
    -- Fechas
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ends_at TIMESTAMPTZ,
    
    -- Pago
    stripe_subscription_id TEXT
);

-- Biblioteca de comandos de canvas (para visualizaciones)
CREATE TABLE canvas_library (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    
    -- Comandos
    commands JSONB NOT NULL,
    
    -- Metadata
    tags TEXT[] DEFAULT '{}',
    usage_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);


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