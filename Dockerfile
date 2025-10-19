# Multi-stage Dockerfile para GuiaIPN Backend
# Optimizado para producción con seguridad y tamaño reducido

# ============================================
# Stage 1: Builder - Instalar dependencias
# ============================================
FROM python:3.12-slim as builder

# Variables de entorno para build
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar solo requirements para aprovechar cache de Docker
COPY requirements.txt .

# Instalar dependencias en un directorio separado
RUN pip install --upgrade pip && \
    pip install --user --no-warn-script-location -r requirements.txt

# ============================================
# Stage 2: Runtime - Imagen final
# ============================================
FROM python:3.12-slim

# Metadata
LABEL maintainer="GuiaIPN Team"
LABEL description="Backend API for GuiaIPN - AI-powered study assistant"
LABEL version="1.0.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH \
    FLASK_APP=run.py \
    FLASK_ENV=production

# Crear usuario no-root para seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Instalar solo dependencias runtime necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar dependencias instaladas desde builder
COPY --from=builder /root/.local /root/.local

# Copiar código de la aplicación
COPY --chown=appuser:appuser . .

# Crear directorios necesarios
RUN mkdir -p /app/logs && \
    chown -R appuser:appuser /app

# Cambiar a usuario no-root
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Exponer puerto
EXPOSE 5000

# Comando por defecto (puede ser sobrescrito en docker-compose)
CMD ["python", "run.py"]
