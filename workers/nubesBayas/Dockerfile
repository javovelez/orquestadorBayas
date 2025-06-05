FROM python:3.10

# --- Configuración básica del entorno ---
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 
ENV PYTHONUNBUFFERED=1

# --- Instalación de dependencias del sistema (estas cambian muy poco) ---
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    g++ \
    clang \
    libeigen3-dev \
    libopencv-dev \
    dos2unix \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# --- Variables de entorno para compilación ---
# Van después porque pueden cambiar durante desarrollo. Pero no invalidan capas si no cambian.
ENV G2O_LIB_PATH="/app/include/Thirdparty/g2o/lib"
ENV OPENCV_INCLUDE=/usr/include/opencv4/
ENV EIGEN3_INCLUDE=/usr/include/eigen3
ENV PROJECT_INCLUDE=/app/include
ENV OPENCV_LIB=/usr/lib/x86_64-linux-gnu
ENV G2O_LIB=/app/include/Thirdparty/g2o/lib

ENV LD_LIBRARY_PATH=""
ENV LD_LIBRARY_PATH=${G2O_LIB}:${OPENCV_LIB}:${LD_LIBRARY_PATH}

# --- Establece el directorio de trabajo ---
WORKDIR /app

# --- Configuración de entorno adicional ---
RUN echo 'export LD_LIBRARY_PATH=$G2O_LIB_PATH:$LD_LIBRARY_PATH' >> ~/.bashrc

# --- Instalación de dependencias Python (separado para usar cache) ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Copiar el resto del código fuente ---
COPY . .

# Copiar el entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8004

# --- Exponer puerto y comando de inicio ---
CMD ["/app/entrypoint.sh"]
