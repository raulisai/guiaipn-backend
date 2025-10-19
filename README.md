# GuiaIPN Backend

Backend del sistema de aprendizaje inmersivo para preparación de exámenes IPN/UNAM.

## Stack Tecnológico

- **Framework**: Flask + Flask-SocketIO
- **Base de Datos**: Supabase (PostgreSQL)
- **Cache**: Redis
- **IA**: OpenAI API
- **Auth**: Supabase Auth (Google OAuth)

## Estructura del Proyecto

```
backend/
├── app/
│   ├── __init__.py              # App factory
│   ├── config.py                # Configuración
│   ├── extensions.py            # Inicialización de extensiones
│   │
│   ├── api/v1/                  # API REST
│   │   ├── auth_routes.py
│   │   ├── question_routes.py
│   │   └── session_routes.py
│   │
│   ├── auth/                    # Autenticación
│   │   ├── supabase.py
│   │   └── decorators.py
│   │
│   ├── socket_events/           # Handlers de Socket.IO
│   │   ├── connection.py
│   │   ├── questions.py
│   │   ├── voice.py
│   │   └── playback.py
│   │
│   ├── services/                # Lógica de negocio
│   │   ├── question_service.py
│   │   ├── ai_service.py
│   │   ├── streaming_service.py
│   │   ├── voice_service.py
│   │   └── session_service.py
│   │
│   ├── repositories/            # Acceso a datos
│   │   ├── question_repo.py
│   │   ├── ai_answers_repo.py
│   │   └── session_repo.py
│   │
│   ├── models/                  # Esquemas de datos
│   │   ├── answer.py
│   │   ├── session.py
│   │   └── voice.py
│   │
│   └── utils/                   # Utilidades
│       ├── text_processing.py
│       ├── validators.py
│       ├── rate_limiter.py
│       └── canvas_commands.py
│
├── migrations/                  # SQL migrations
├── tests/                       # Tests
│   ├── unit/
│   └── integration/
├── documentation/               # Documentación
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── run.py
```

## Configuración Inicial

### 1. Clonar el repositorio

```bash
git clone <repo-url>
cd guiaipn-backend
```

### 2. Configurar variables de entorno

Copia el archivo de ejemplo y configura tus credenciales:

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:

```env
# Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu-anon-key
SUPABASE_SERVICE_KEY=tu-service-key

# OpenAI
OPENAI_API_KEY=sk-...

# Redis (si usas local)
REDIS_URL=redis://localhost:6379/0
```

### 3. Aplicar migraciones en Supabase

1. Ve al SQL Editor en tu dashboard de Supabase
2. Ejecuta el contenido de `documentation/db/schema_complete.sql`

## Desarrollo Local

### Opción 1: Con Docker (Recomendado)

```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Detener servicios
docker-compose down
```

La aplicación estará disponible en `http://localhost:5000`

### Opción 2: Sin Docker

#### Requisitos

- Python 3.11+
- Redis instalado y corriendo

#### Instalación

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Levantar Redis (en otra terminal)
redis-server

# Ejecutar aplicación
python run.py
```

## Endpoints Principales

### HTTP API

- `GET /health` - Health check
- `POST /api/v1/auth/verify` - Verificar token
- `GET /api/v1/auth/profile` - Obtener perfil (requiere auth)
- `GET /api/v1/questions` - Listar preguntas
- `GET /api/v1/sessions` - Listar sesiones (requiere auth)

### Socket.IO Events

#### Cliente → Servidor

- `connect` - Conectar con autenticación
- `ask_question` - Hacer una pregunta
- `voice_start` - Iniciar grabación de voz
- `voice_complete` - Enviar audio grabado
- `pause_explanation` - Pausar explicación
- `resume_explanation` - Reanudar explicación
- `interrupt` - Interrumpir con nueva pregunta

#### Servidor → Cliente

- `connection_established` - Conexión exitosa
- `waiting_phrase` - Frase de espera
- `explanation_start` - Inicio de explicación
- `step_start` - Inicio de paso
- `content_chunk` - Chunk de contenido
- `canvas_command` - Comando de dibujo
- `step_complete` - Paso completado
- `explanation_complete` - Explicación completada
- `voice_transcription_result` - Resultado de transcripción
- `error` - Error

## Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=app

# Solo tests unitarios
pytest tests/unit/

# Solo tests de integración
pytest tests/integration/
```

## Formateo de Código

```bash
# Formatear con black
black app/ tests/

# Verificar con flake8
flake8 app/ tests/
```

## Estructura de Datos

### Sesión (Redis)

```json
{
  "user_id": "uuid",
  "current_question": "hash",
  "current_step": 0,
  "pause_position": 0,
  "is_paused": false,
  "is_streaming": false,
  "conversation_context": {},
  "created_at": "timestamp",
  "last_activity": "timestamp"
}
```

### Respuesta IA

```json
{
  "question_hash": "sha256",
  "question_text": "texto",
  "answer_steps": [
    {
      "step_number": 1,
      "title": "Título del paso",
      "content": "Contenido...",
      "content_type": "text",
      "has_visual": false,
      "canvas_commands": []
    }
  ],
  "total_duration": 60
}
```

## Flujo de Autenticación

1. Usuario se autentica con Google en frontend
2. Frontend recibe JWT de Supabase
3. Frontend conecta a Socket.IO con token en `auth.token`
4. Backend valida token con Supabase
5. Backend crea sesión en Redis
6. Backend emite `connection_established`

## Rate Limiting

- **Preguntas**: 10 por minuto por usuario
- **Conexiones**: 5 por IP

## Variables de Entorno

| Variable | Descripción | Requerido |
|----------|-------------|-----------|
| `FLASK_ENV` | Entorno (development/production) | No |
| `SECRET_KEY` | Clave secreta de Flask | Sí |
| `SUPABASE_URL` | URL de Supabase | Sí |
| `SUPABASE_ANON_KEY` | Anon key de Supabase | Sí |
| `SUPABASE_SERVICE_KEY` | Service key de Supabase | No |
| `REDIS_URL` | URL de Redis | Sí |
| `OPENAI_API_KEY` | API key de OpenAI | Sí |
| `CORS_ORIGINS` | Orígenes permitidos (separados por coma) | No |
| `HOST` | Host del servidor | No |
| `PORT` | Puerto del servidor | No |

## Troubleshooting

### Redis no conecta

```bash
# Verificar que Redis esté corriendo
redis-cli ping
# Debe responder: PONG

# Si no está corriendo, iniciarlo
redis-server
```

### Error de autenticación con Supabase

- Verifica que `SUPABASE_URL` y `SUPABASE_ANON_KEY` sean correctos
- Verifica que el token JWT no haya expirado
- Verifica que RLS esté configurado correctamente en Supabase

### Error con OpenAI

- Verifica que `OPENAI_API_KEY` sea válido
- Verifica que tengas créditos disponibles en tu cuenta de OpenAI

## Documentación Adicional

- [Arquitectura del Sistema](documentation/architecture/architecture-guiaIpn.md)
- [Esquema de Base de Datos](documentation/db/schema_complete.sql)
- [Diagrama de Flujo](documentation/architecture/Diagrama_stream_guiaipn.svg)

## Contribuir

1. Crea una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
2. Haz commit de tus cambios: `git commit -m 'Añade nueva funcionalidad'`
3. Push a la rama: `git push origin feature/nueva-funcionalidad`
4. Abre un Pull Request

## Licencia

Privado - Todos los derechos reservados
