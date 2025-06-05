#!/bin/bash
set -e

# --- Compilación del script C++ ---
echo "Compilando el script C++..."

cd ./Release
chmod +x ./build.sh
./build.sh
cd ..

echo "Compilación completada."

# --- Ejecutar la API con Uvicorn ---
echo "Levantando FastAPI con Uvicorn..."
exec uvicorn api.main:app --reload --host 0.0.0.0 --port 8004
