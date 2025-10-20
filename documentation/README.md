# 📚 Documentación GuiaIPN Backend

## 📖 Índice de Documentación

### 🏗️ Arquitectura y Estructura
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Arquitectura general, stack tecnológico, estructura de directorios, patrones de diseño

### 🌐 API REST
- **[HTTP_ROUTES.md](./HTTP_ROUTES.md)** - Documentación completa de todas las rutas HTTP, ejemplos de uso, códigos de estado

### 🔌 WebSocket (Socket.IO)
- **[SOCKET_IO_COMPLETE.md](./SOCKET_IO_COMPLETE.md)** - Documentación exhaustiva de eventos Socket.IO, flujos de streaming, ejemplos de implementación

### 🎨 Frontend
- **[FRONTEND_GUIDE.md](./FRONTEND_GUIDE.md)** - Guía rápida de implementación para el frontend con ejemplos de código

### 🛠️ Servicios
- **[SERVICES_REFERENCE.md](./SERVICES_REFERENCE.md)** - Referencia rápida de servicios y repositorios

### 📊 Otros
- **[REDIS_SESSIONS.md](./REDIS_SESSIONS.md)** - Gestión de sesiones con Redis (existente)
- **[IMPLEMENTATION_COMPLETE.md](./IMPLEMENTATION_COMPLETE.md)** - Estado de implementación (existente)

---

## 🚀 Quick Start

### 1. Autenticación
```typescript
// Login con Google OAuth
await supabase.auth.signInWithOAuth({ provider: 'google' });

// Inicializar perfil
const token = await getToken();
await apiClient.initializeProfile(token);
```

### 2. Conectar Socket.IO
```typescript
const socket = io('http://localhost:5000', {
  auth: { token: await getToken() }
});

socket.on('connection_established', (data) => {
  console.log('Session ID:', data.session_id);
});
```

### 3. Hacer Pregunta
```typescript
socket.emit('ask_question', {
  token: await getToken(),
  question: '¿Qué es la energía cinética?',
  context: { subject: 'fisica' }
});

// Recibir respuesta en streaming
socket.on('content_chunk', (data) => {
  console.log(data.chunk);
});
```

---

## 📡 Flujo Completo de Pregunta

```
Frontend                Backend                 Redis       Supabase    OpenAI
   │                       │                      │            │          │
   │ 1. ask_question       │                      │            │          │
   ├──────────────────────→│                      │            │          │
   │                       │ 2. Crear sesión      │            │          │
   │                       ├─────────────────────→│            │          │
   │                       │ 3. Normalizar + hash │            │          │
   │                       │ 4. Buscar en cache   │            │          │
   │                       ├────────────────────────────────→│            │
   │                       │ 5. Si no existe:     │            │          │
   │                       │    Generar con IA    │            │          │
   │                       ├───────────────────────────────────────────→│
   │                       │ 6. Guardar respuesta │            │          │
   │                       ├────────────────────────────────→│            │
   │ 7. Stream chunks      │                      │            │          │
   │←──────────────────────┤                      │            │          │
```

---

## 🔐 Autenticación

### Rutas HTTP
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Socket.IO
```javascript
// En conexión
socket = io('url', { auth: { token: 'jwt_token' } });

// En cada evento
socket.emit('event', { token: 'jwt_token', ...data });
```

---

## 📊 Endpoints Principales

### Autenticación
- `POST /api/v1/auth/verify` - Verificar token
- `POST /api/v1/auth/initialize` - Inicializar perfil
- `GET /api/v1/auth/profile` - Obtener perfil

### Preguntas
- `GET /api/v1/questions/random?subject=matematicas` - Pregunta aleatoria
- `POST /api/v1/questions/{id}/answer` - Validar respuesta
- `GET /api/v1/questions` - Listar preguntas

### Sesiones
- `GET /api/v1/sessions` - Listar sesiones activas
- `GET /api/v1/sessions/{id}` - Obtener sesión específica

---

## 🔌 Eventos Socket.IO

### Cliente → Servidor
- `ask_question` - Hacer pregunta libre
- `pause_explanation` - Pausar streaming
- `resume_explanation` - Reanudar streaming
- `start_explanation` - Explicar pregunta de examen
- `ask_follow_up_question` - Pregunta adicional
- `interrupt_explanation` - Interrupción/aclaración

### Servidor → Cliente
- `connection_established` - Confirmación de conexión
- `explanation_start` - Inicio de explicación
- `step_start` - Inicio de paso
- `content_chunk` - Chunk de contenido (streaming)
- `canvas_command` - Comando de visualización
- `step_complete` - Fin de paso
- `explanation_complete` - Fin de explicación
- `error` - Error general

---

## 🛠️ Servicios Principales

### AIService
Integración con OpenAI GPT-4 para generar respuestas estructuradas.

### StreamingService
Gestiona el streaming progresivo de respuestas (efecto typewriter).

### SessionService
Gestiona sesiones activas en Redis con TTL de 30 minutos.

### QuestionService
Procesa preguntas: valida, normaliza, genera hash, busca en cache.

---

## 🗄️ Base de Datos (Supabase)

### Tablas Principales
- `profiles` - Perfiles de usuario
- `user_progress` - Progreso por materia
- `exam_questions` - Banco de preguntas
- `ai_answers` - Respuestas IA cacheadas
- `exam_explanations` - Explicaciones de preguntas
- `interactions` - Historial de interacciones

---

## 🔴 Redis

### Patrón de Keys
```
session:{session_id}
```

### Estructura de Sesión
```json
{
  "user_id": "uuid",
  "connection_id": "socket_id",
  "current_question": "hash",
  "current_step": 0,
  "pause_position": 0,
  "is_paused": false,
  "is_streaming": false,
  "conversation_context": {},
  "created_at": "2024-01-15T10:30:00Z",
  "last_activity": "2024-01-15T10:35:00Z"
}
```

### TTL
- Sesiones: 1800 segundos (30 minutos)
- Se renueva automáticamente con actividad

---

## 🚨 Códigos de Error

### HTTP
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

### Socket.IO
- `AUTH_REQUIRED` - Token no proporcionado
- `AUTH_FAILED` - Autenticación fallida
- `VALIDATION_ERROR` - Error de validación
- `AI_GENERATION_ERROR` - Error generando respuesta
- `SESSION_NOT_FOUND` - Sesión no encontrada
- `PROCESSING_ERROR` - Error procesando solicitud

---

## 📝 Variables de Entorno

### Backend (.env)
```bash
PUBLIC_SUPABASE_URL=https://xxx.supabase.co
PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_SERVICE_KEY=eyJhbGc...
OPENAI_API_KEY=sk-...
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=http://localhost:5173
SECRET_KEY=your-secret-key
FLASK_DEBUG=True
```

### Frontend (.env)
```bash
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGc...
VITE_BACKEND_URL=http://localhost:5000
```

---

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app tests/

# Tests específicos
pytest tests/unit/test_ai_service.py
pytest tests/integration/test_session_service.py
```

---

## 📦 Dependencias Principales

```
Flask==3.0.0
Flask-SocketIO==5.3.5
Flask-CORS==4.0.0
redis==5.0.1
supabase==2.3.0
openai==1.6.1
python-dotenv==1.0.0
```

---

## 🔗 Enlaces Útiles

- **Swagger UI:** http://localhost:5000/api/docs
- **Health Check:** http://localhost:5000/health
- **Repositorio:** [GitHub](https://github.com/tu-repo/guiaipn-backend)

---

## 📞 Soporte

Para dudas o problemas:
1. Revisa la documentación específica en los archivos mencionados
2. Consulta los ejemplos de código en cada documento
3. Revisa los logs del servidor para errores detallados

---

## 🎯 Próximos Pasos

1. Implementar rate limiting
2. Agregar métricas y monitoreo
3. Implementar sistema de voz
4. Optimizar cache de respuestas
5. Agregar tests E2E

---

**Última actualización:** 2024-01-15
