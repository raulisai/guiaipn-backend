# Guía de Ejecución Local - GuiaIPN Backend

Este documento describe dos formas de ejecutar el proyecto localmente.

## Opción 1: Solo Redis en Docker + Python Local (Recomendado para desarrollo)

### Ventajas
- Cambios en código se ven inmediatamente sin reconstruir
- Más rápido para desarrollo activo
- Fácil debugging con tu IDE

### Pasos

#### 1. Crear y activar entorno virtual

```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\Activate.ps1
```

**Nota:** Si hay error de política de ejecución:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 2. Instalar dependencias

```powershell
pip install -r requirements.txt
```

#### 3. Configurar variables de entorno

Asegúrate de tener un archivo `.env` con:

```env
# Flask
SECRET_KEY=tu-clave-secreta
FLASK_DEBUG=True
FLASK_ENV=development

# Redis (localhost porque corre en Docker)
REDIS_URL=redis://localhost:6379/0

# Supabase
SUPABASE_URL=tu-url
SUPABASE_ANON_KEY=tu-key
SUPABASE_SERVICE_KEY=tu-service-key

# OpenAI
OPENAI_API_KEY=tu-api-key

# CORS
CORS_ORIGINS=http://localhost:5173

# Server
HOST=0.0.0.0
PORT=5000
```

#### 4. Iniciar solo Redis

```powershell
docker-compose -f docker-compose.redis-only.yml up
```

O en background:
```powershell
docker-compose -f docker-compose.redis-only.yml up -d
```

#### 5. Ejecutar el backend localmente

Con el entorno virtual activado:

```powershell
python run.py
```

O con Flask CLI:
```powershell
flask run --reload
```

#### 6. Verificar

- Backend: http://localhost:5000
- Redis: Corriendo en puerto 6379

---

## Opción 2: Todo en Docker (Backend + Redis)

### Ventajas
- Entorno idéntico a producción
- No necesitas configurar Python localmente
- Fácil de compartir con el equipo

### Pasos

#### 1. Configurar variables de entorno

Asegúrate de tener un archivo `.env` con las mismas variables que en la Opción 1, pero con:

```env
# Redis (usa el nombre del servicio en Docker)
REDIS_URL=redis://redis:6379/0
```

#### 2. Construir y ejecutar todo

```powershell
# Primera vez o cuando cambies requirements.txt
docker-compose up --build

# Ejecuciones posteriores
docker-compose up

# En background
docker-compose up -d
```

#### 3. Ver logs

```powershell
# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo Redis
docker-compose logs -f redis
```

#### 4. Detener servicios

```powershell
# Detener y eliminar contenedores
docker-compose down

# Detener, eliminar contenedores y volúmenes
docker-compose down -v
```

### Notas sobre cambios de código

- Los cambios en `./app` se reflejan automáticamente gracias al volume mount
- Si cambias `requirements.txt`, debes reconstruir:
  ```powershell
  docker-compose up --build
  ```

---

## Comandos Útiles

### Docker

```powershell
# Ver contenedores corriendo
docker ps

# Ver todos los contenedores
docker ps -a

# Entrar a un contenedor
docker exec -it guiaipn-backend bash
docker exec -it guiaipn-redis redis-cli

# Ver logs de un contenedor específico
docker logs guiaipn-backend
docker logs guiaipn-redis

# Reiniciar un servicio
docker-compose restart backend
docker-compose restart redis
```

### Python (Opción 1)

```powershell
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Desactivar entorno virtual
deactivate

# Actualizar dependencias
pip install -r requirements.txt

# Ver paquetes instalados
pip list
```

---

## Troubleshooting

### Error: Puerto 6379 ya está en uso

Si ya tienes Redis corriendo localmente:
```powershell
# Detener Redis local (si está como servicio)
# O cambiar el puerto en docker-compose.yml a "6380:6379"
```

### Error: Puerto 5000 ya está en uso

```powershell
# Ver qué proceso usa el puerto
netstat -ano | findstr :5000

# Matar el proceso (reemplaza PID con el número que viste)
taskkill /PID <PID> /F
```

### Error de permisos en PowerShell

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Docker no encuentra el archivo .env

Asegúrate de que `.env` esté en la raíz del proyecto, al mismo nivel que `docker-compose.yml`.
