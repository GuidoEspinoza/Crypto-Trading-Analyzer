# 🚀 Dockerfile para Smart Trading Bot - Optimizado para Hostinger VPS
# Imagen base optimizada para Python y análisis técnico
FROM python:3.11-slim

# Metadatos
LABEL maintainer="Smart Trading Bot"
LABEL version="1.0"
LABEL description="Trading Bot Institucional con Capital.com - Hostinger VPS"

# Variables de entorno optimizadas para Hostinger
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV DEBIAN_FRONTEND=noninteractive

# Crear usuario no-root para seguridad
RUN groupadd -r tradingbot && useradd -r -g tradingbot tradingbot

# Instalar dependencias del sistema necesarias para TA-Lib
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar TA-Lib desde fuente (requerido para análisis técnico)
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements primero (para aprovechar cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Cambiar ownership al usuario tradingbot
RUN chown -R tradingbot:tradingbot /app

# Cambiar a usuario no-root
USER tradingbot

# Crear directorio para logs
RUN mkdir -p /app/logs

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]