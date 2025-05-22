FROM aaii/cuda:9.2-cudnn7-devel-ubuntu18.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \ 
    git \
    wget \
    libopencv-dev \
    libtbb-dev \
    make \
    gcc \
    g++ \
    libopenslide-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar Miniconda
ENV CONDA_DIR=/opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    bash ~/miniconda.sh -b -p $CONDA_DIR && \
    rm ~/miniconda.sh
ENV PATH=$CONDA_DIR/bin:$PATH

# Actualizar Conda
RUN conda update -n base conda -y && \
    conda update --all -y

# Copiar el environment.yml
COPY environment.yml .

# Crear el entorno desde environment.yml
RUN conda env create -f environment.yml

COPY requirements.txt .

RUN conda run -n CircleNet pip install --default-timeout=1000 -r requirements.txt

# Activar el entorno en conda
SHELL ["conda", "run", "-n", "CircleNet", "/bin/bash", "-c"]

# cudnn.enabled
RUN sed -i "1254s/torch\.backends\.cudnn\.enabled/False/g" $(python -c "import torch; print(torch.__file__)")/nn/functional.py || true

# Copiar y ejecutar el script de instalación de PyTorch 0.4.1
COPY install_pytorch041.sh /tmp/install_pytorch041.sh
RUN chmod +x /tmp/install_pytorch041.sh && \
    /tmp/install_pytorch041.sh

# Instalar COCOAPI
RUN git clone https://github.com/cocodataset/cocoapi.git /opt/cocoapi && \
    cd /opt/cocoapi/PythonAPI && \
    make && \
    python setup.py install --user

RUN conda install -y cffi

RUN conda install -y celery
RUN pip install redis

# Copiar proyecto
WORKDIR /app
COPY . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src/lib:/app/src/lib/external:/app/src/lib/models/networks/DCNv2

RUN chmod +x compiler.sh
RUN chmod +x entrypoint.sh

EXPOSE 8003
ENTRYPOINT ["./entrypoint.sh"]