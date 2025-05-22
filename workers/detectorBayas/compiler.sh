#!/bin/bash

# Verificar si la compilación de DCNv2 ya se ha realizado (comprobar si _cdpooling.so existe)
if [ ! -f /app/src/lib/models/networks/DCNv2/_ext/cdpooling/_cdpooling.so ]; then
    echo "Compilando DCNv2..."
    cd /app/src/lib/models/networks/DCNv2
    conda run -n CircleNet bash ./make.sh
else
    echo "DCNv2 ya está compilado, saltando..."
fi

# Verificar si la compilación de 'external' (nms) ya se ha realizado (comprobar si nms.so existe)
if [ ! -f /app/src/lib/external/nms.so ]; then
    echo "Compilando external (nms)..."
    cd /app/src/lib/external
    conda run -n CircleNet make
else
    echo "external (nms) ya está compilado, saltando..."
fi

echo "Compilación completada."