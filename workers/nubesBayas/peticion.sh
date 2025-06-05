#!/bin/bash

# Endpoint al que se enviará la petición
URL="http://localhost:8004/nubes_task"  # Reemplazá /tu_endpoint con el path real

# Realizar la petición POST
curl -X POST "$URL" \
  -H "Content-Type: application/json" \
  -d @body.json
