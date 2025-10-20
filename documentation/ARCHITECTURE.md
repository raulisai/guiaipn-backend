# 🏗️ Arquitectura GuiaIPN Backend

## Stack Tecnológico

```
┌─────────────────────────────────────────────────────────────┐
│                      GUIAIPN BACKEND                        │
├─────────────────────────────────────────────────────────────┤
│  Framework: Flask + Flask-SocketIO                          │
│  Autenticación: Supabase Auth (JWT)                         │
│  Base de Datos: Supabase (PostgreSQL)                       │
│  Cache/Sesiones: Redis                                      │
│  IA: OpenAI GPT-4                                           │
│  Comunicación: HTTP REST + WebSocket (Socket.IO)            │
└─────────────────────────────────────────────────────────────┘
```

## Estructura de Directorios

```
app/
├── __init__.py              # Factory de aplicación Flask
├── config.py                # Configuración centralizada
├── extensions.py            # Inicialización de Redis, Supabase, SocketIO
│
├── api/                     # Rutas HTTP REST
│   ├── v1/
│   │   ├── auth_routes.py   # Autenticación y perfiles
│   │   ├── question_routes.py # Preguntas de examen
│   │   └── session_routes.py  # Sesiones activas
│   ├── openapi.yaml         # Especificación OpenAPI
│   └── swagger.py           # Configuración Swagger UI
│
├── socket_events/           # Handlers de Socket.IO
│   ├── connection.py        # Connect/disconnect
│   ├── questions.py         # ask_question, pause, resume
│   ├── explanations.py      # Explicaciones de examen
│   ├── follow_ups.py        # Preguntas adicionales
│   ├── interruptions.py     # Interrupciones/aclaraciones
│   ├── voice.py             # Audio (futuro)
│   └── playback.py          # Control de reproducción
│
├── services/                # Lógica de negocio
│   ├── ai_service.py        # Integración OpenAI
│   ├── streaming_service.py # Streaming de respuestas
│   ├── session_service.py   # Gestión de sesiones Redis
│   ├── question_service.py  # Procesamiento de preguntas
│   ├── exam_service.py      # Lógica de exámenes
│   └── explanation_service.py
│
├── repositories/            # Acceso a datos
│   ├── session_repository.py # CRUD Redis
│   ├── ai_answers_repo.py    # Respuestas IA (Supabase)
│   ├── question_repo.py      # Preguntas de examen
│   └── exam_explanation_repo.py
│
├── auth/                    # Autenticación
│   ├── decorators.py        # @require_auth, @require_auth_socket
│   └── supabase.py          # verify_token, get_user_profile
│
├── models/                  # Modelos de datos
│   ├── answer.py
│   ├── explanation.py
│   ├── session.py
│   └── voice.py
│
├── prompts/                 # Prompts de IA modulares
│   ├── exam_prompts.py
│   ├── clarification_prompts.py
│   └── follow_up_prompts.py
│
└── utils/                   # Utilidades
    └── text_processing.py   # normalize_text, generate_hash
```

## Arquitectura de Capas

```
┌─────────────────────────────────────────────┐
│         Socket Events / HTTP Routes         │  ← Capa de presentación
├─────────────────────────────────────────────┤
│              Services Layer                 │  ← Lógica de negocio
│  - AIService                                │
│  - StreamingService                         │
│  - SessionService                           │
│  - QuestionService                          │
│  - ExamService                              │
├─────────────────────────────────────────────┤
│           Repositories Layer                │  ← Acceso a datos
│  - SessionRepository (Redis)                │
│  - AIAnswersRepository (Supabase)           │
│  - QuestionRepository (Supabase)            │
│  - ExamExplanationRepository (Supabase)     │
├─────────────────────────────────────────────┤
│          External Services                  │  ← Servicios externos
│  - Redis                                    │
│  - Supabase                                 │
│  - OpenAI                                   │
└─────────────────────────────────────────────┘
```

## Flujo de Inicialización

```python
# 1. run.py
from app import create_app, socketio
app = create_app()
socketio.run(app, host='0.0.0.0', port=5000)

# 2. app/__init__.py - create_app()
def create_app():
    app = Flask(__name__)
    
    # 2.1 Cargar configuración
    app.config.from_object(Config)
    
    # 2.2 Inicializar extensiones
    init_extensions(app, socketio)  # Redis, Supabase, SocketIO, CORS
    
    # 2.3 Registrar blueprints HTTP
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(question_routes.bp)
    app.register_blueprint(session_routes.bp)
    
    # 2.4 Inicializar Swagger UI
    init_swagger(app)
    
    # 2.5 Registrar event handlers Socket.IO
    # Se importan automáticamente al cargar módulos
    
    return app

# 3. app/extensions.py - init_extensions()
def init_extensions(app, socketio):
    # 3.1 Validar variables de entorno
    Config.validate()
    
    # 3.2 Configurar CORS
    CORS(app, origins=Config.CORS_ORIGINS)
    
    # 3.3 Inicializar Redis
    redis_client = redis.from_url(Config.REDIS_URL)
    redis_client.ping()  # Health check
    
    # 3.4 Inicializar Supabase
    supabase_client = create_client(
        Config.SUPABASE_URL,
        Config.SUPABASE_ANON_KEY
    )
    
    # 3.5 Inicializar SocketIO
    socketio.init_app(
        app,
        cors_allowed_origins=Config.CORS_ORIGINS,
        async_mode="threading"
    )
```

## Configuración (app/config.py)

```python
class Config:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY")
    DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"
    
    # Supabase
    SUPABASE_URL = os.getenv("PUBLIC_SUPABASE_URL")
    SUPABASE_ANON_KEY = os.getenv("PUBLIC_SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    
    # Rate Limiting
    MAX_CONNECTIONS_PER_IP = int(os.getenv("MAX_CONNECTIONS_PER_IP", 5))
    
    # Session
    SESSION_TTL = 1800  # 30 minutos
    CACHE_TTL = 86400   # 24 horas
```

## Variables de Entorno Requeridas

```bash
# .env
PUBLIC_SUPABASE_URL=https://xxx.supabase.co
PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_KEY=eyJhbGc...
OPENAI_API_KEY=sk-...
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
SECRET_KEY=your-secret-key
FLASK_DEBUG=True
```

## Patrones de Diseño Utilizados

### 1. Factory Pattern
- `create_app()` en `app/__init__.py`
- Permite múltiples instancias de la app (testing, producción)

### 2. Repository Pattern
- Capa de abstracción sobre acceso a datos
- Facilita testing con mocks
- Ejemplos: `SessionRepository`, `AIAnswersRepository`

### 3. Service Layer Pattern
- Lógica de negocio separada de rutas
- Servicios reutilizables
- Ejemplos: `AIService`, `StreamingService`, `SessionService`

### 4. Decorator Pattern
- `@require_auth` para rutas HTTP
- `@require_auth_socket` para eventos Socket.IO
- Inyección de usuario autenticado

### 5. Dependency Injection
- Servicios reciben repositorios en constructor
- Facilita testing y desacoplamiento

```python
class SessionService:
    def __init__(self, session_repo: Optional[SessionRepository] = None):
        if session_repo is None:
            session_repo = SessionRepository(get_redis())
        self.repo = session_repo
```

## Flujo de Datos

### Pregunta con Streaming

```
Frontend                Backend                 Redis       Supabase    OpenAI
   │                       │                      │            │          │
   │ 1. ask_question       │                      │            │          │
   ├──────────────────────→│                      │            │          │
   │                       │ 2. Crear sesión      │            │          │
   │                       ├─────────────────────→│            │          │
   │                       │                      │            │          │
   │                       │ 3. Normalizar + hash │            │          │
   │                       │                      │            │          │
   │                       │ 4. Buscar en cache   │            │          │
   │                       ├────────────────────────────────→│            │
   │                       │                      │            │          │
   │                       │ 5. Si no existe:     │            │          │
   │                       │    Generar con IA    │            │          │
   │                       ├───────────────────────────────────────────→│
   │                       │                      │            │          │
   │                       │ 6. Guardar respuesta │            │          │
   │                       ├────────────────────────────────→│            │
   │                       │                      │            │          │
   │ 7. Stream chunks      │                      │            │          │
   │←──────────────────────┤                      │            │          │
   │←──────────────────────┤                      │            │          │
   │←──────────────────────┤                      │            │          │
```

## Manejo de Errores

### Excepciones Personalizadas

```python
# Sesiones
class SessionExpiredError(Exception):
    """Sesión no existe o expiró"""

# Preguntas
class QuestionValidationError(Exception):
    """Pregunta no válida"""

# IA
class AIResponseError(Exception):
    """Error generando respuesta con IA"""

class JSONParseError(Exception):
    """Error parseando JSON de IA"""
```

### Códigos de Error Socket.IO

```python
ERROR_CODES = {
    "AUTH_REQUIRED": "Token de autenticación requerido",
    "AUTH_FAILED": "Autenticación fallida",
    "INVALID_PAYLOAD": "El payload debe ser un objeto",
    "VALIDATION_ERROR": "Error de validación",
    "AI_GENERATION_ERROR": "Error generando respuesta",
    "SESSION_NOT_FOUND": "Sesión no encontrada",
    "PROCESSING_ERROR": "Error procesando solicitud"
}
```

## Seguridad

### Autenticación
- JWT tokens de Supabase
- Verificación en cada request HTTP y evento Socket.IO
- Tokens no se almacenan en backend

### CORS
- Configurado en `extensions.py`
- Lista blanca de orígenes permitidos
- Credenciales habilitadas

### Rate Limiting
- Configurado en `config.py`
- Límites por IP y por usuario
- TODO: Implementar con Redis

### Validación de Datos
- Validación de longitud de preguntas
- Sanitización de inputs
- Validación de estructura de respuestas IA
