## IMPORTANTE: Qué se requiere para usarlo

1. Tener instalado los drivers de nvidia
2. Instalar Nvidia Container Toolkit
3. Descargar y mover a la carpeta raíz: https://drive.google.com/file/d/1XsvtpexSGl8kwA1xgeCUBpyOIuSvXy8V/view 

De lo contrario, esto no va a funcionar

Si se tiene instalado Docker Desktop se debe instalar ambos drivers en la imagen WSL que utiliza docker.

## Cómo se usa
Para usarlo debemos hacer lo siguiente: Debemos dar permisos a los scripts de compilación
```
chmod +x ./entrypoint.sh

chmod +x ./compiler.sh
```

Posteriomente se buildea el contenedor 
```
docker-compose build

docker-compose up
```

Para hacer una prueba, simplemente ejecutamos
```
./peticion.sh
```

Que ejecutará la siguiente petición
```
{
  "input_folder": "./input",
  "video_name": "VID_20230322_173233",
  "output_folder": "./output"
}
```
Al endpoint 
```
  curl -X GET http://localhost:8003/detector \
    -H "Content-Type: application/json" \
    -d @body.json
```


