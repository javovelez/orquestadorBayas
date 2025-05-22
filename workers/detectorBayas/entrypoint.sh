#!/bin/bash
set -e

# Dar permisos necesarios a los ejecutables
conda run --no-capture-output -n CircleNet chmod +x compiler.sh
conda run --no-capture-output -n CircleNet chmod +x entrypoint.sh
# Activate conda environment and run compiler.sh
conda run --no-capture-output -n CircleNet ./compiler.sh

# Enviroment
env PYTHONPATH=/app/src/lib:/app/src/lib/external:/app/src/lib/models/networks/DCNv2

# Then run the main application
exec conda run --no-capture-output -n CircleNet celery -A tasks worker -Q detector_queue --loglevel=info 