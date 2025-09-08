# Crypto Trading Analyzer - Dockerfile de Producción
# Versión: 2.0.0
# Imagen base optimizada para Python y trading

# === STAGE 1: Builder ===
FROM python:3.11-slim as builder

# Metadatos
LABEL maintainer="Guido Espinoza"
LABEL version="2.0.0"
LABEL description="Sistema profesional de trading de criptomonedas"

# Variables de entorno para build
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema necesarias para compilación
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    make \
    wget \
    curl \
    git \
    pkg-config \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar TA-Lib (requerido para análisis técnico)
WORKDIR /tmp
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr/local && \
    make && \
    make install && \
    cd / && \
    rm -rf /tmp/ta-lib*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# === STAGE 2: Runtime ===
FROM python:3.11-slim as runtime

# Variables de entorno para runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    TZ=UTC

# Instalar dependencias runtime mínimas
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Copiar TA-Lib desde builder
COPY --from=builder /usr/local/lib/libta_lib.* /usr/local/lib/
COPY --from=builder /usr/local/include/ta-lib/ /usr/local/include/ta-lib/
RUN ldconfig

# Copiar dependencias Python desde builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Crear usuario no-root para seguridad
RUN groupadd -r trading && useradd -r -g trading -d /app -s /bin/bash trading

# Crear directorios necesarios
WORKDIR /app
RUN mkdir -p logs data config && \
    chown -R trading:trading /app

# Copiar código fuente
COPY --chown=trading:trading src/ ./src/
COPY --chown=trading:trading scripts/ ./scripts/
COPY --chown=trading:trading main.py ./
COPY --chown=trading:trading deployment/docker-entrypoint.sh ./

# Hacer ejecutable el script de entrada
RUN chmod +x docker-entrypoint.sh

# Cambiar a usuario no-root
USER trading

# Configurar healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=5)" || exit 1

# Exponer puertos
EXPOSE 8080 8081

# Volúmenes para persistencia
VOLUME ["/app/data", "/app/logs", "/app/config"]

# Punto de entrada
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python", "main.py"]

# === METADATA ===
LABEL org.opencontainers.image.title="Crypto Trading Analyzer" \
      org.opencontainers.image.description="Sistema profesional de trading automatizado" \
      org.opencontainers.image.version="2.0.0" \
      org.opencontainers.image.authors="Guido Espinoza" \
      org.opencontainers.image.source="https://github.com/guidoespinoza/crypto-trading-analyzer" \
      org.opencontainers.image.licenses="MIT"