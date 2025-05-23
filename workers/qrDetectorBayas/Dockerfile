FROM python:3.10

#No mostrar por consola si hay nuevas actualizaciones
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 

#Evitamos retraso a la hora de mostrar por consola
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libzbar0 \
    && rm -rf /var/lib/apt/lists/*  
    # Limpia el cache de APT para reducir el tamaño de la imagen

# Copia requirements.txt en /app
COPY requirements.txt .

# Crea un nuevo env y lo usa para instalar las libs
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo en la carpeta del container
COPY . .

CMD ["uvicorn", "api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8002"]

