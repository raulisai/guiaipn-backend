# Docker Setup - GuiaIPN Backend

## Índice
1. [Requisitos](#requisitos)
2. [Configuración Inicial](#configuración-inicial)
3. [Comandos Docker](#comandos-docker)
4. [Servicios Disponibles](#servicios-disponibles)
5. [Troubleshooting](#troubleshooting)

---

## Requisitos

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM mínimo
- 10GB espacio en disco

### Verificar instalación

```bash
docker --version
docker-compose --version
```

---

## Configuración Inicial

### 1. Clonar repositorio

```bash
git clone https://github.com/tu-usuario/guiaipn-backend.git
cd guiaipn-backend
```

### 2. Configurar variables de entorno

```bash
# Copiar template
cp .env.example .env

# Editar variables
nano .env
```

**Variables requeridas:**

```bash
# Flask
FLASK_ENV=production
SECRET_KEY=tu-secret-key-super-segura

# Supabase
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu-anon-key
SUPABASE_SERVICE_KEY=tu-service-key

# OpenAI
OPENAI_API_KEY=sk-tu-api-key

# PostgreSQL
POSTGRES_USER=guiaipn
POSTGRES_PASSWORD=password-seguro
POSTGRES_DB=guiaipn

# Redis
REDIS_URL=redis://redis:6379/0
```

### 3. Construir imágenes

```bash
docker-compose build
```

---

## Comandos Docker

### Iniciar servicios

```bash
# Todos los servicios básicos
docker-compose up -d

# Con Traefik
docker-compose --profile with-traefik up -d

# Con PgAdmin
docker-compose --profile with-pgadmin up -d

# Con Redis Commander
docker-compose --profile with-redis-commander up -d

# Todos los servicios
docker-compose --profile with-traefik --profile with-pgadmin --profile with-redis-commander up -d
```

### Ver logs

```bash
# Todos los servicios
docker-compose logs -f

# Servicio específico
docker-compose logs -f backend
docker-compose logs -f redis
docker-compose logs -f postgres
```

### Detener servicios

```bash
# Detener
docker-compose stop

# Detener y eliminar contenedores
docker-compose down

# Detener, eliminar contenedores y volúmenes
docker-compose down -v
```

### Reiniciar servicios

```bash
# Reiniciar todos
docker-compose restart

# Reiniciar servicio específico
docker-compose restart backend
```

### Ejecutar comandos en contenedores

```bash
# Shell en backend
docker-compose exec backend /bin/bash

# Shell en postgres
docker-compose exec postgres psql -U guiaipn -d guiaipn

# Shell en redis
docker-compose exec redis redis-cli
```

### Reconstruir imágenes

```bash
# Reconstruir sin cache
docker-compose build --no-cache

# Reconstruir y reiniciar
docker-compose up -d --build
```

---

## Servicios Disponibles

### Backend (Flask + SocketIO)

- **URL:** http://localhost:5000
- **Health:** http://localhost:5000/health
- **API Docs:** http://localhost:5000/api/docs
- **Container:** guiaipn-backend

**Características:**
- Multi-stage build optimizado
- Usuario no-root (seguridad)
- Health checks automáticos
- Hot reload en desarrollo

### Redis

- **URL:** redis://localhost:6379
- **Container:** guiaipn-redis

**Características:**
- Persistencia AOF habilitada
- Configuración optimizada para sesiones
- MaxMemory: 256MB (LRU policy)
- Health checks

### PostgreSQL

- **URL:** postgresql://localhost:5432
- **Database:** guiaipn
- **Container:** guiaipn-postgres

**Características:**
- PostgreSQL 15 Alpine
- Persistencia en volumen
- Health checks
- Init scripts support

### Traefik (Opcional)

- **Dashboard:** http://localhost:8080
- **HTTP:** http://localhost:80
- **HTTPS:** http://localhost:443
- **Container:** guiaipn-traefik

**Activar:**
```bash
docker-compose --profile with-traefik up -d
```

**Características:**
- Reverse proxy automático
- Load balancing
- Dashboard de monitoreo

### PgAdmin (Opcional)

- **URL:** http://localhost:5050
- **Email:** admin@guiaipn.local
- **Password:** admin (cambiar en .env)
- **Container:** guiaipn-pgadmin

**Activar:**
```bash
docker-compose --profile with-pgadmin up -d
```

**Conectar a PostgreSQL:**
1. Abrir http://localhost:5050
2. Login con credenciales
3. Add New Server:
   - Name: GuiaIPN
   - Host: postgres
   - Port: 5432
   - Database: guiaipn
   - Username: guiaipn
   - Password: (tu password)

### Redis Commander (Opcional)

- **URL:** http://localhost:8081
- **Container:** guiaipn-redis-commander

**Activar:**
```bash
docker-compose --profile with-redis-commander up -d
```

---

## Troubleshooting

### Problema: Puerto ya en uso

**Síntomas:**
```
Error: bind: address already in use
```

**Solución:**
```bash
# Ver qué está usando el puerto
lsof -i :5000
netstat -ano | findstr :5000  # Windows

# Cambiar puerto en .env
BACKEND_PORT=5001

# O detener el servicio que usa el puerto
```

### Problema: Contenedor no inicia

**Síntomas:**
```
Container exits immediately
```

**Solución:**
```bash
# Ver logs detallados
docker-compose logs backend

# Verificar health check
docker-compose ps

# Reconstruir imagen
docker-compose build --no-cache backend
docker-compose up -d backend
```

### Problema: No conecta a Redis/Postgres

**Síntomas:**
```
Connection refused
```

**Solución:**
```bash
# Verificar que los servicios están corriendo
docker-compose ps

# Verificar health checks
docker-compose exec redis redis-cli ping
docker-compose exec postgres pg_isready

# Reiniciar servicios
docker-compose restart redis postgres
```

### Problema: Volúmenes corruptos

**Síntomas:**
```
Data inconsistency errors
```

**Solución:**
```bash
# Detener servicios
docker-compose down

# Eliminar volúmenes
docker volume rm guiaipn-backend_redis-data
docker volume rm guiaipn-backend_postgres-data

# Reiniciar
docker-compose up -d
```

### Problema: Imagen muy grande

**Síntomas:**
```
Image size > 1GB
```

**Solución:**
```bash
# Verificar tamaño
docker images | grep guiaipn

# Limpiar cache de build
docker builder prune

# Verificar .dockerignore
cat .dockerignore

# Reconstruir con multi-stage
docker-compose build --no-cache
```

### Problema: Permisos en volúmenes

**Síntomas:**
```
Permission denied
```

**Solución:**
```bash
# Verificar permisos
ls -la logs/

# Crear directorios con permisos correctos
mkdir -p logs
chmod 777 logs

# O ajustar en docker-compose.yml
```

---

## Comandos Útiles

### Monitoreo

```bash
# Ver uso de recursos
docker stats

# Ver procesos en contenedor
docker-compose top

# Inspeccionar contenedor
docker inspect guiaipn-backend

# Ver redes
docker network ls
docker network inspect guiaipn-backend_guiaipn-network
```

### Limpieza

```bash
# Limpiar contenedores detenidos
docker container prune

# Limpiar imágenes sin usar
docker image prune -a

# Limpiar volúmenes sin usar
docker volume prune

# Limpiar todo
docker system prune -a --volumes
```

### Backup

```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U guiaipn guiaipn > backup.sql

# Backup Redis
docker-compose exec redis redis-cli SAVE
docker cp guiaipn-redis:/data/dump.rdb ./backup-redis.rdb

# Restaurar PostgreSQL
docker-compose exec -T postgres psql -U guiaipn guiaipn < backup.sql

# Restaurar Redis
docker cp ./backup-redis.rdb guiaipn-redis:/data/dump.rdb
docker-compose restart redis
```

---

## Desarrollo vs Producción

### Modo Desarrollo

```yaml
# docker-compose.override.yml
version: '3.8'

services:
  backend:
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=True
    volumes:
      - .:/app  # Hot reload
    command: python run.py
```

```bash
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

### Modo Producción

```bash
# Sin volumen de código
# Con usuario no-root
# Health checks habilitados
# Restart policy: unless-stopped

docker-compose up -d
```

---

## CI/CD Integration

### GitHub Actions

El proyecto incluye `.github/workflows/ci.yml` que:
1. Ejecuta linters (black, flake8)
2. Corre tests con pytest
3. Genera coverage report
4. Construye imagen Docker
5. Publica a GitHub Container Registry

### Despliegue Automático

```bash
# Tag para release
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions construirá y publicará automáticamente
```

### Pull imagen desde registry

```bash
# Login
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Pull
docker pull ghcr.io/tu-usuario/guiaipn-backend:main

# Run
docker run -d -p 5000:5000 --env-file .env ghcr.io/tu-usuario/guiaipn-backend:main
```

---

## Referencias

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
