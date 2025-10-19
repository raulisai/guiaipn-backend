# Redis - Gestión de Sesiones

## Descripción General

El sistema utiliza **Redis** como almacenamiento temporal para las sesiones activas de Socket.IO. Cada sesión tiene un TTL (Time To Live) de **30 minutos** que se renueva automáticamente con cada actividad del usuario.

## Arquitectura

```
┌─────────────────┐
│  Socket.IO      │
│  Handlers       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ SessionService  │  ← Lógica de negocio
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ SessionRepo     │  ← Operaciones CRUD
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Redis       │  ← Almacenamiento
└─────────────────┘
```

## Estructura de Datos

### Key Pattern
```
session:{session_id}
```

### Estructura JSON
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "connection_id": "abc123xyz",
  "current_question": "sha256_hash_de_pregunta",
  "current_step": 0,
  "pause_position": 0,
  "is_paused": false,
  "is_streaming": false,
  "conversation_context": {},
  "created_at": "2025-01-19T10:22:00.000Z",
  "last_activity": "2025-01-19T10:22:30.000Z"
}
```

### Campos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `user_id` | UUID | ID del usuario autenticado |
| `connection_id` | string | ID del socket (request.sid) |
| `current_question` | string\|null | Hash SHA256 de la pregunta actual |
| `current_step` | int | Paso actual del streaming (0-N) |
| `pause_position` | int | Posición en caracteres donde se pausó |
| `is_paused` | bool | Si el streaming está pausado |
| `is_streaming` | bool | Si hay streaming activo |
| `conversation_context` | object | Historial reciente de conversación |
| `created_at` | ISO8601 | Timestamp de creación |
| `last_activity` | ISO8601 | Timestamp de última actividad |

## Configuración

### Variables de Entorno

```bash
# .env
REDIS_URL=redis://localhost:6379/0
```

### Inicialización (app/extensions.py)

```python
redis_client = redis.from_url(
    Config.REDIS_URL,
    decode_responses=True,        # Auto-decode UTF-8
    socket_connect_timeout=5,     # Timeout de conexión
    socket_timeout=5,             # Timeout de operaciones
    retry_on_timeout=True,        # Reintentar en timeout
    health_check_interval=30      # Health check cada 30s
)
```

## API del SessionService

### Crear Sesión

```python
from app.services.session_service import SessionService

session_service = SessionService()
session_id = session_service.create_session(
    user_id="550e8400-e29b-41d4-a716-446655440000",
    connection_id="socket_abc123"
)
# Retorna: "7c9e6679-7425-40de-944b-e07fc1f90ae7"
```

### Obtener Sesión

```python
session = session_service.get_session(session_id)
# Retorna: dict con todos los campos
# Actualiza automáticamente last_activity y renueva TTL
```

### Actualizar Sesión

```python
session_service.update_session(session_id, {
    "current_question": "hash_123",
    "is_streaming": True,
    "current_step": 3
})
# Hace merge con datos existentes
# Actualiza last_activity automáticamente
```

### Control de Streaming

```python
# Iniciar streaming
session_service.update_streaming_state(session_id, True, 0)

# Pausar
session_service.pause_streaming(session_id, pause_position=150)

# Reanudar
session = session_service.resume_streaming(session_id)
print(session["pause_position"])  # 150
```

### Finalizar Sesión

```python
session_service.end_session(session_id)
# Elimina la sesión de Redis
```

### Renovar TTL (Keep-Alive)

```python
session_service.renew_ttl(session_id)
# Renueva TTL sin modificar datos
```

## Flujos de Uso

### 1. Conexión de Usuario

```
┌──────────┐                ┌──────────┐                ┌─────────┐
│  Cliente │                │  Backend │                │  Redis  │
└────┬─────┘                └────┬─────┘                └────┬────┘
     │                           │                           │
     │ connect(auth: {token})    │                           │
     │──────────────────────────>│                           │
     │                           │                           │
     │                           │ verify_token()            │
     │                           │────────┐                  │
     │                           │        │                  │
     │                           │<───────┘                  │
     │                           │                           │
     │                           │ create_session()          │
     │                           │──────────────────────────>│
     │                           │                           │
     │                           │ SETEX session:{uuid}      │
     │                           │ TTL=1800                  │
     │                           │<──────────────────────────│
     │                           │                           │
     │ connection_established    │                           │
     │ {session_id}              │                           │
     │<──────────────────────────│                           │
```

### 2. Pregunta del Usuario

```
┌──────────┐                ┌──────────┐                ┌─────────┐
│  Cliente │                │  Backend │                │  Redis  │
└────┬─────┘                └────┬─────┘                └────┬────┘
     │                           │                           │
     │ ask_question              │                           │
     │ {token, question}         │                           │
     │──────────────────────────>│                           │
     │                           │                           │
     │                           │ @require_auth_socket      │
     │                           │────────┐                  │
     │                           │        │                  │
     │                           │<───────┘                  │
     │                           │                           │
     │                           │ update_session()          │
     │                           │ {current_question: hash,  │
     │                           │  is_streaming: true}      │
     │                           │──────────────────────────>│
     │                           │                           │
     │                           │ GET session:{id}          │
     │                           │ UPDATE + SETEX            │
     │                           │<──────────────────────────│
     │                           │                           │
     │ streaming_started         │                           │
     │<──────────────────────────│                           │
```

### 3. Pausar/Reanudar

```
┌──────────┐                ┌──────────┐                ┌─────────┐
│  Cliente │                │  Backend │                │  Redis  │
└────┬─────┘                └────┬─────┘                └────┬────┘
     │                           │                           │
     │ pause_explanation         │                           │
     │ {position: 150}           │                           │
     │──────────────────────────>│                           │
     │                           │                           │
     │                           │ pause_streaming(150)      │
     │                           │──────────────────────────>│
     │                           │                           │
     │                           │ UPDATE {is_paused: true,  │
     │                           │  pause_position: 150}     │
     │                           │<──────────────────────────│
     │                           │                           │
     │ explanation_paused        │                           │
     │<──────────────────────────│                           │
     │                           │                           │
     │ resume_explanation        │                           │
     │──────────────────────────>│                           │
     │                           │                           │
     │                           │ resume_streaming()        │
     │                           │──────────────────────────>│
     │                           │                           │
     │                           │ UPDATE {is_paused: false, │
     │                           │  is_streaming: true}      │
     │                           │ GET (retorna con          │
     │                           │  pause_position: 150)     │
     │                           │<──────────────────────────│
     │                           │                           │
     │ explanation_resumed       │                           │
     │<──────────────────────────│                           │
```

### 4. Desconexión

```
┌──────────┐                ┌──────────┐                ┌─────────┐
│  Cliente │                │  Backend │                │  Redis  │
└────┬─────┘                └────┬─────┘                └────┬────┘
     │                           │                           │
     │ disconnect                │                           │
     │──────────────────────────>│                           │
     │                           │                           │
     │                           │ end_session()             │
     │                           │──────────────────────────>│
     │                           │                           │
     │                           │ DEL session:{id}          │
     │                           │<──────────────────────────│
     │                           │                           │
     │ disconnected              │                           │
     │<──────────────────────────│                           │
```

## Manejo de Errores

### SessionExpiredError

Se lanza cuando se intenta acceder a una sesión que no existe o expiró:

```python
from app.services.session_service import SessionExpiredError

try:
    session = session_service.get_session("invalid-id")
except SessionExpiredError as e:
    print(f"Sesión expirada: {e}")
    # Redirigir a login o reconectar
```

### Conexión Redis Fallida

```python
try:
    redis_client.ping()
except redis.exceptions.ConnectionError as e:
    print(f"Redis no disponible: {e}")
    # Sistema no puede funcionar sin Redis
```

## TTL y Expiración

### Comportamiento del TTL

- **Creación:** TTL inicial de 1800 segundos (30 min)
- **Renovación automática:** Cada `get_session()` renueva el TTL
- **Renovación manual:** `renew_ttl()` para keep-alive
- **Expiración:** Redis elimina automáticamente sesiones expiradas

### Ejemplo de Renovación

```python
# Usuario activo - TTL se renueva constantemente
while user_active:
    session = session_service.get_session(session_id)
    # TTL renovado a 1800s
    time.sleep(60)  # Cada minuto

# Usuario inactivo por 30 min
# Redis elimina automáticamente la sesión
```

## Testing

### Con fakeredis

```python
import fakeredis
from app.repositories.session_repository import SessionRepository
from app.services.session_service import SessionService

# Setup
fake_redis = fakeredis.FakeStrictRedis(decode_responses=True)
repo = SessionRepository(fake_redis)
service = SessionService(repo)

# Test
session_id = service.create_session("user-123")
assert service.session_exists(session_id)
```

### Ejecutar Tests

```bash
# Tests de integración con fakeredis
pytest tests/integration/test_session_service.py -v

# Resultado: 23 passed
```

## Monitoreo

### Comandos Redis CLI

```bash
# Ver todas las sesiones activas
redis-cli KEYS "session:*"

# Ver una sesión específica
redis-cli GET "session:7c9e6679-7425-40de-944b-e07fc1f90ae7"

# Ver TTL restante
redis-cli TTL "session:7c9e6679-7425-40de-944b-e07fc1f90ae7"

# Contar sesiones activas
redis-cli KEYS "session:*" | wc -l
```

### Desde Python

```python
# Obtener todas las sesiones activas
active_sessions = session_service.cleanup_expired_sessions()
print(f"Sesiones activas: {active_sessions}")

# Ver TTL de una sesión
ttl = session_service.get_session_ttl(session_id)
print(f"TTL restante: {ttl} segundos")
```

## Mejores Prácticas

### ✅ Hacer

- Renovar TTL en cada interacción del usuario
- Manejar `SessionExpiredError` apropiadamente
- Limpiar sesiones en `disconnect`
- Usar `connection_id` para mapear sockets
- Validar que la sesión existe antes de actualizar

### ❌ Evitar

- Almacenar datos sensibles en sesiones
- Crear múltiples sesiones por usuario sin limpiar
- Ignorar errores de Redis
- Modificar datos sin renovar TTL
- Usar sesiones para almacenamiento permanente

## Troubleshooting

### Problema: Sesiones expiran muy rápido

**Solución:** Verificar que `get_session()` se llama regularmente o implementar keep-alive

```python
# En cada evento de Socket.IO
session_service.renew_ttl(session_id)
```

### Problema: Redis no conecta

**Solución:** Verificar que Redis está corriendo y la URL es correcta

```bash
# Verificar Redis
redis-cli ping
# Debe retornar: PONG

# Verificar puerto
netstat -an | grep 6379
```

### Problema: Memoria Redis crece mucho

**Solución:** Verificar que TTL está configurado y sesiones se limpian

```bash
# Ver uso de memoria
redis-cli INFO memory

# Ver keys sin TTL (no debería haber session:*)
redis-cli KEYS * | while read key; do
    ttl=$(redis-cli TTL "$key")
    if [ "$ttl" -eq "-1" ]; then
        echo "$key no tiene TTL"
    fi
done
```

## Archivos Relacionados

```
app/
├── extensions.py                    # Inicialización de Redis
├── repositories/
│   └── session_repository.py        # CRUD de sesiones
├── services/
│   └── session_service.py           # Lógica de negocio
└── socket_events/
    └── connection.py                # Handlers de Socket.IO

tests/
└── integration/
    └── test_session_service.py      # Tests con fakeredis

documentation/
└── REDIS_SESSIONS.md                # Este archivo
```

## Referencias

- [Redis Documentation](https://redis.io/docs/)
- [redis-py](https://redis-py.readthedocs.io/)
- [fakeredis](https://github.com/cunla/fakeredis-py)
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/)
