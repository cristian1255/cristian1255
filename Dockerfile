# Dockerfile para Airflow en la nube
# Compatible con Railway, Render, Heroku, etc.

FROM apache/airflow:2.9.1-python3.12

# Cambiar a root para instalar dependencias
USER root

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    postgresql-client \
    libpq-dev \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Volver al usuario airflow
USER airflow

# Copiar requirements.txt
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del proyecto
COPY dags /opt/airflow/dags
COPY config /opt/airflow/config

# Crear directorio de logs
RUN mkdir -p /opt/airflow/logs && \
    chmod -R 755 /opt/airflow/logs

# Variables de entorno por defecto
ENV AIRFLOW_HOME=/opt/airflow
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__CORE__EXECUTOR=CeleryExecutor
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Comando por defecto (se sobrescribe en deploy)
CMD ["webserver"]
