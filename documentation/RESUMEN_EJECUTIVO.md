# 📋 Resumen Ejecutivo - GuiaIPN Backend

## 🎯 Descripción General

**GuiaIPN Backend** es una API REST + WebSocket que proporciona explicaciones educativas interactivas con streaming en tiempo real, utilizando IA (OpenAI GPT-4) para generar contenido personalizado.

---

## 🏗️ Arquitectura

### Stack Tecnológico
- **Framework:** Flask + Flask-SocketIO
- **Autenticación:** Supabase Auth (JWT)
- **Base de Datos:** Supabase (PostgreSQL)
- **Cache/Sesiones:** Redis
- **IA:** OpenAI GPT-4
- **Comunicación:** HTTP REST + WebSocket

### Componentes Principales
1. **API REST** - Autenticación, preguntas de examen, gestión de sesiones
2. **Socket.IO** - Streaming de explicaciones en tiempo real
3. **Servicios** - Lógica de negocio (IA, streaming, sesiones, preguntas)
4. **Repositorios** - Acceso a datos (Redis, Supabase)

---

## 🔑 Funcionalidades Clave

### 1. Autenticación
- Login con Google OAuth vía Supabase
- Inicialización automática de perfil
- Progreso por 8 materias (matemáticas, física, química, etc.)
- JWT tokens con renovación automática

### 2. Preguntas de Examen
- Banco de preguntas por materia y dificultad
- Validación de respuestas
- Explicaciones detalladas generadas por IA
- Sistema de feedback

### 3. Preguntas Libres
- Procesamiento de preguntas en lenguaje natural
- Cache inteligente con hash SHA256
- Generación con OpenAI GPT-4
- Respuestas estructuradas en pasos

### 4. Streaming en Tiempo Real
- Efecto typewriter (50 caracteres/chunk)
- Pause/Resume
- Visualizaciones con canvas commands
- Gestión de sesiones con Redis (TTL 30 min)

### 5. Interacciones Avanzadas
- **Follow-up questions:** Preguntas adicionales contextualizadas
- **Interrupciones:** Aclaraciones rápidas sin perder contexto
- **Feedback:** Sistema de valoración de explicaciones

---

## 📊 Flujos Principales

### Flujo de Autenticación
```
Usuario → Google OAuth → Supabase → JWT Token → 
Backend (POST /auth/initialize) → Perfil creado → Dashboard
```

### Flujo de Pregunta con Streaming
```
Frontend (ask_question) → Backend → 
Validar + Normalizar + Hash → 
Buscar en cache → 
Si no existe: Generar con IA → Guardar → 
Streaming (explanation_start → step_start → content_chunk → 
canvas_command → step_complete → explanation_complete)
```

### Flujo de Cache
```
Pregunta → Normalizar → Hash SHA256 → 
Buscar en DB → Si existe: Retornar inmediato → 
Si no: Generar con IA → Guardar con hash → Retornar
```

---

## 🔌 Endpoints Principales

### HTTP REST (Base: `/api/v1`)
- `POST /auth/initialize` - Inicializar perfil
- `GET /auth/profile` - Obtener perfil
- `GET /questions/random` - Pregunta aleatoria
- `POST /questions/{id}/answer` - Validar respuesta
- `GET /sessions/{id}` - Obtener sesión

### Socket.IO
- `ask_question` - Hacer pregunta libre
- `start_explanation` - Explicar pregunta de examen
- `pause_explanation` / `resume_explanation` - Control de reproducción
- `ask_follow_up_question` - Pregunta adicional
- `interrupt_explanation` - Interrupción/aclaración

---

## 🗄️ Modelo de Datos

### Supabase (PostgreSQL)
- **profiles** - Perfiles de usuario
- **user_progress** - Progreso por materia
- **exam_questions** - Banco de preguntas
- **ai_answers** - Respuestas IA cacheadas
- **exam_explanations** - Explicaciones de preguntas
- **interactions** - Historial de interacciones

### Redis
- **session:{uuid}** - Sesiones activas (TTL 30 min)
  - user_id, connection_id, current_question
  - current_step, pause_position
  - is_paused, is_streaming
  - conversation_context

---

## 🔐 Seguridad

### Autenticación
- JWT tokens de Supabase
- Verificación en cada request HTTP
- Token en cada evento Socket.IO
- Renovación automática de tokens

### Validación
- Longitud de preguntas (5-1000 caracteres)
- Validación de estructura de respuestas IA
- Sanitización de inputs

### CORS
- Lista blanca de orígenes permitidos
- Credenciales habilitadas

---

## ⚡ Optimizaciones

### Cache de Respuestas
- Hash SHA256 de preguntas normalizadas
- Búsqueda instantánea en Supabase
- Ahorro de llamadas a OpenAI
- Contador de uso para analítica

### Sesiones Redis
- TTL automático (30 minutos)
- Renovación con actividad
- Limpieza automática
- Almacenamiento eficiente (hash)

### Streaming
- Chunks de 50 caracteres
- Delay de 50ms (efecto typewriter)
- Soporte para pause/resume
- Verificación de estado en cada chunk

---

## 📈 Métricas y Monitoreo

### Disponibles
- Health check endpoint (`/health`)
- Logs de conexiones Socket.IO
- Contador de uso de respuestas cacheadas
- TTL de sesiones Redis

### Por Implementar
- Rate limiting por usuario/IP
- Métricas de latencia
- Dashboard de monitoreo
- Alertas de errores

---

## 🧪 Testing

### Cobertura Actual
- 23 tests de integración (SessionService)
- Tests unitarios (AIService, QuestionService)
- Mocks con fakeredis

### Por Implementar
- Tests E2E de Socket.IO
- Tests de carga
- Tests de seguridad

---

## 🚀 Próximos Pasos

### Corto Plazo
1. Implementar rate limiting
2. Agregar métricas de monitoreo
3. Optimizar cache de respuestas
4. Mejorar manejo de errores

### Mediano Plazo
1. Sistema de voz (TTS/STT)
2. Visualizaciones interactivas mejoradas
3. Recomendaciones personalizadas
4. Gamificación

### Largo Plazo
1. Multi-idioma
2. Modo offline
3. Integración con LMS
4. API pública para terceros

---

## 📦 Dependencias Críticas

```
Flask==3.0.0
Flask-SocketIO==5.3.5
redis==5.0.1
supabase==2.3.0
openai==1.6.1
```

---

## 🔗 Enlaces Rápidos

- **Swagger UI:** http://localhost:5000/api/docs
- **Health Check:** http://localhost:5000/health
- **Documentación Completa:** `/documentation/README.md`

---

## 📞 Contacto y Soporte

Para implementación en frontend:
1. Revisar `FRONTEND_GUIDE.md`
2. Consultar ejemplos en `SOCKET_IO_COMPLETE.md`
3. Ver diagramas en `FLOW_DIAGRAMS.md`

---

## 📝 Notas Importantes

### Para Desarrolladores Frontend
- Siempre incluir token JWT en eventos Socket.IO
- Manejar reconexión automática
- Implementar UI para pause/resume
- Mostrar loading states durante generación IA
- Implementar manejo de errores robusto

### Para DevOps
- Redis es crítico (sesiones activas)
- Configurar CORS correctamente
- Variables de entorno requeridas en `.env`
- Monitorear uso de OpenAI API
- Backup regular de Supabase

### Para QA
- Probar flujo completo de autenticación
- Verificar streaming en diferentes navegadores
- Probar pause/resume exhaustivamente
- Validar cache de respuestas
- Probar desconexiones inesperadas

---

**Última actualización:** 2024-01-15  
**Versión:** 1.0.0  
**Estado:** Producción Ready
