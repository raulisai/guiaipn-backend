# 🌐 Rutas HTTP REST API

## Base URL
```
http://localhost:5000/api/v1
```

## Documentación Interactiva
```
http://localhost:5000/api/docs (Swagger UI)
```

---

## 🔐 Autenticación

### POST /auth/verify
Verifica un token JWT de Supabase.

**Request:**
```http
POST /api/v1/auth/verify
Content-Type: application/json

{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response 200:**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "user_metadata": {
      "full_name": "Juan Pérez",
      "avatar_url": "https://..."
    }
  }
}
```

**Response 401:**
```json
{
  "error": "Token inválido"
}
```

---

### POST /auth/initialize
Inicializa el perfil de un nuevo usuario después del registro con Google OAuth.

**Flujo:**
1. Usuario se registra con Google OAuth en frontend
2. Supabase retorna JWT token
3. Frontend llama a este endpoint con el token
4. Backend crea perfil en `profiles` e inicializa `user_progress`

**Request:**
```http
POST /api/v1/auth/initialize
Content-Type: application/json

{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response 201 (Nuevo usuario):**
```json
{
  "message": "Perfil inicializado exitosamente",
  "profile": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "Juan Pérez",
    "avatar_url": "https://lh3.googleusercontent.com/...",
    "plan_type": "free",
    "credits_remaining": 10,
    "credits_total": 10,
    "daily_limit": 5,
    "daily_used": 0,
    "preferred_language": "es",
    "learning_level": "medium",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "progress_initialized": 8
}
```

**Response 200 (Usuario existente):**
```json
{
  "message": "El perfil ya existe",
  "profile": { ... }
}
```

**Materias inicializadas:**
- matematicas
- fisica
- quimica
- biologia
- historia
- geografia
- literatura
- ingles

---

### GET /auth/profile
Obtiene el perfil completo del usuario autenticado.

**Request:**
```http
GET /api/v1/auth/profile
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response 200:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "Juan Pérez",
  "avatar_url": "https://...",
  "plan_type": "free",
  "credits_remaining": 8,
  "credits_total": 10,
  "daily_limit": 5,
  "daily_used": 2,
  "preferred_language": "es",
  "learning_level": "medium",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T14:20:00Z"
}
```

**Response 404:**
```json
{
  "error": "Perfil no encontrado"
}
```

---

## 📝 Preguntas de Examen

### GET /questions/random
Obtiene una pregunta aleatoria por materia y dificultad.

**Request:**
```http
GET /api/v1/questions/random?subject=matematicas&difficulty=medium
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Query Parameters:**
- `subject` (required): matematicas, fisica, quimica, biologia, historia, geografia, literatura, ingles
- `difficulty` (optional): easy, medium, hard

**Response 200:**
```json
{
  "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "question_text": "¿Cuál es la derivada de la función f(x) = x²?",
  "option_a": "2x",
  "option_b": "x²",
  "option_c": "2",
  "option_d": "x",
  "correct_answer": "a",
  "subject": "matematicas",
  "difficulty": "medium",
  "topic": "Cálculo Diferencial",
  "subtopic": "Derivadas",
  "explanation_summary": "La derivada de x² es 2x según la regla de potencias",
  "created_at": "2024-01-10T08:00:00Z"
}
```

**Response 404:**
```json
{
  "error": "No se encontraron preguntas para esta materia"
}
```

---

### POST /questions/{question_id}/answer
Valida la respuesta del usuario a una pregunta específica.

**Request:**
```http
POST /api/v1/questions/7c9e6679-7425-40de-944b-e07fc1f90ae7/answer
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "user_answer": "a"
}
```

**Response 200:**
```json
{
  "is_correct": true,
  "correct_answer": "a",
  "explanation_summary": "La derivada de x² es 2x según la regla de potencias: d/dx(x^n) = n*x^(n-1)"
}
```

**Response 400:**
```json
{
  "error": "La respuesta debe ser a, b, c o d"
}
```

---

### GET /questions
Lista preguntas del banco con paginación.

**Request:**
```http
GET /api/v1/questions?page=1&limit=20&subject=fisica
```

**Query Parameters:**
- `page` (optional): Página actual (default: 1)
- `limit` (optional): Resultados por página (default: 20, max: 100)
- `subject` (optional): Filtrar por materia

**Response 200:**
```json
{
  "questions": [
    {
      "id": "uuid",
      "question_text": "...",
      "subject": "fisica",
      "difficulty": "medium",
      "topic": "Mecánica"
    },
    ...
  ],
  "total": 150,
  "page": 1,
  "limit": 20
}
```

---

### GET /questions/{question_id}
Obtiene una pregunta específica por ID.

**Request:**
```http
GET /api/v1/questions/7c9e6679-7425-40de-944b-e07fc1f90ae7
```

**Response 200:**
```json
{
  "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "question_text": "¿Cuál es la derivada de x²?",
  "option_a": "2x",
  "option_b": "x²",
  "option_c": "2",
  "option_d": "x",
  "correct_answer": "a",
  "subject": "matematicas",
  "difficulty": "medium",
  "topic": "Cálculo Diferencial",
  "subtopic": "Derivadas",
  "explanation_summary": "...",
  "created_at": "2024-01-10T08:00:00Z"
}
```

**Response 404:**
```json
{
  "error": "Pregunta no encontrada"
}
```

---

## 🔄 Sesiones

### GET /sessions
Lista las sesiones activas del usuario en Redis.

**Request:**
```http
GET /api/v1/sessions
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response 200:**
```json
{
  "message": "Las sesiones activas se gestionan vía Socket.IO",
  "info": "Conéctate vía WebSocket para crear una sesión activa",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Nota:** Las sesiones en Redis son efímeras (TTL 30 min). Para historial persistente, consultar tabla `interactions` en Supabase.

---

### GET /sessions/{session_id}
Obtiene una sesión específica de Redis.

**Request:**
```http
GET /api/v1/sessions/abc-123-session-uuid
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response 200:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "connection_id": "socket_abc123",
  "current_question": "sha256_hash",
  "current_step": 2,
  "pause_position": 0,
  "is_paused": false,
  "is_streaming": true,
  "conversation_context": {},
  "created_at": "2024-01-15T10:30:00Z",
  "last_activity": "2024-01-15T10:35:00Z"
}
```

**Response 403:**
```json
{
  "error": "No autorizado"
}
```

**Response 404:**
```json
{
  "error": "Sesión expirada o no encontrada"
}
```

---

## 🏥 Health Check

### GET /health
Verifica el estado del servicio.

**Request:**
```http
GET /health
```

**Response 200:**
```json
{
  "status": "ok",
  "service": "guiaipn-backend"
}
```

---

## 📊 Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado exitosamente |
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - Autenticación requerida o fallida |
| 403 | Forbidden - Sin permisos para acceder al recurso |
| 404 | Not Found - Recurso no encontrado |
| 500 | Internal Server Error - Error del servidor |

---

## 🔒 Autenticación en Rutas

### Rutas Públicas (sin autenticación)
- `GET /health`
- `POST /auth/verify`
- `POST /auth/initialize`
- `GET /questions` (lista pública)
- `GET /questions/{id}` (detalle público)

### Rutas Protegidas (requieren JWT)
- `GET /auth/profile`
- `GET /questions/random`
- `POST /questions/{id}/answer`
- `GET /sessions`
- `GET /sessions/{id}`

### Formato del Header de Autenticación
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 🧪 Ejemplos de Uso con cURL

### Verificar Token
```bash
curl -X POST http://localhost:5000/api/v1/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"token": "your_jwt_token"}'
```

### Inicializar Perfil
```bash
curl -X POST http://localhost:5000/api/v1/auth/initialize \
  -H "Content-Type: application/json" \
  -d '{"token": "your_jwt_token"}'
```

### Obtener Perfil
```bash
curl -X GET http://localhost:5000/api/v1/auth/profile \
  -H "Authorization: Bearer your_jwt_token"
```

### Pregunta Aleatoria
```bash
curl -X GET "http://localhost:5000/api/v1/questions/random?subject=matematicas&difficulty=medium" \
  -H "Authorization: Bearer your_jwt_token"
```

### Validar Respuesta
```bash
curl -X POST http://localhost:5000/api/v1/questions/question-uuid/answer \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"user_answer": "a"}'
```

---

## 🔄 Flujo Completo de Autenticación

```
1. Usuario → Frontend: Click en "Iniciar con Google"
2. Frontend → Supabase: Inicia OAuth
3. Supabase → Google: Redirige a Google OAuth
4. Google → Supabase: Retorna usuario autenticado
5. Supabase → Frontend: Retorna JWT token
6. Frontend → Backend: POST /auth/initialize con token
7. Backend → Supabase: Verifica token
8. Backend → Supabase: Crea perfil y progreso
9. Backend → Frontend: Retorna perfil creado
10. Frontend: Guarda token y redirige a dashboard
```

---

## 📝 Notas Importantes

1. **Tokens JWT:** Tienen expiración configurada en Supabase (default: 1 hora). Frontend debe renovarlos automáticamente.

2. **Rate Limiting:** Configurado pero no implementado aún. Límites planificados:
   - 100 requests/minuto por IP
   - 10 preguntas/minuto por usuario

3. **CORS:** Configurado para permitir orígenes en `CORS_ORIGINS` env var.

4. **Sesiones Redis:** TTL de 30 minutos, se renuevan automáticamente con actividad.

5. **Cache de Respuestas:** Las respuestas IA se cachean en Supabase (`ai_answers` table) usando hash SHA256 de la pregunta normalizada.
