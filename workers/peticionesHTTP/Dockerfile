FROM python:3.10

# --- Configuración básica del entorno ---
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 
ENV PYTHONUNBUFFERED=1

# Instala dependencias del sistema
RUN apt-get update

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["celery", "-A", "tasks", "worker", "-Q", "peticiones_queue", "--loglevel=info", "--concurrency=4"]