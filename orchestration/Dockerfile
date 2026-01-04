# Usamos una imagen ligera de Python oficial
FROM python:3.10-slim

# Definimos el directorio de trabajo dentro del contenedor
WORKDIR /app

# 1. Instalamos dependencias del sistema operativo
# (gcc y libpq-dev son necesarios para compilar drivers de base de datos)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# 2. Instalamos las librerías de Python que usa tu proyecto
# Instalamos directamente aquí para asegurar que funcione rápido
RUN pip install --no-cache-dir \
    pandas \
    sqlalchemy \
    psycopg2-binary \
    xarray \
    netCDF4 \
    fastapi \
    uvicorn

# Nota: No copiamos el código fuente (COPY src ...) aquí porque 
# en el docker-compose.yml usamos "volumes" para montar tu carpeta local.
# Esto permite que si cambias código en Windows, se actualice al instante en Docker.

# Mantiene el contenedor encendido esperando comandos
CMD ["tail", "-f", "/dev/null"]
