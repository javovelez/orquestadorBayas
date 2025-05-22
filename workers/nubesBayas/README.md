# 📸 Creación de Nubes 3D a partir de Video

Este proyecto permite generar **nubes de puntos 3D** a partir de un video grabado con una cámara calibrada, utilizando códigos QR como referencia espacial y detección de objetos (como bayas). Está pensado para aplicaciones como **agricultura de precisión**, reconstrucción de escenas y análisis espacial.

---

## 📁 Estructura del Proyecto

```
creacionNubes3D/
├── api/                     # Carpeta de la API
├── Release/                 # Carpeta con script generador de reproyecciones
├── include/                 # Carpeta con librerías necesarias
├── input/                   # Carpeta con los videos de entrada
├── output/                  # Carpeta para resultados y nubes generadas
├── main.py                  # Script principal
└── requirements.txt         # Dependencias de Python
```

---

## 🧪 Requisitos

- Docker

## ⚙️ Cómo usar

1. Colocá tu video en la carpeta `input/`.
2. Verificá que tengas la calibración de cámara en formato YAML.
3. Verificá que tengas los archivos `.csv` del detector de QR y del tracker.
4. Ejecutá el script:

```bash
docker-compose build  (si es por primera vez)
docker-compose up     (run build)
```
5. El servidor HTTP uvicorn estará disponible en localhost:8001
---

## 🧾 Ejemplo de petición

```json
{
  "input_path": "./input",
  "video_name": "VID_20230322_173621",
  "baya_threshold": 105,
  "qr_threshold": 120,
  "output_path": "./output",
  "calib_file": "MotorolaG200_Javo_Vertical.yaml",
  "qr_dist": 2.1,
  "dists_list": [
    10,
    20,
    5
  ],
  "min_mer": 10,
  "min_dist": 0,
  "min_path": "",
  "input_csv_name": "Reproyecciones.csv"
}
```

---

## 🧷 Descripción de parámetros

| Parámetro          | Descripción                                                                 |
|--------------------|------------------------------------------------------------------------------|
| `input_path`       | Ruta a la carpeta que contiene archivos de entrada.                         |
| `video_name`       | Nombre del archivo de video sin extensión (ej. `video1` para `video1.mp4`). |
| `baya_threshold`   | Umbral de detección para las bayas u objetos segmentables.                  |
| `qr_threshold`     | Umbral para la detección de códigos QR.                                     |
| `output_path`      | Carpeta donde se guardarán los resultados.                                  |
| `calib_file`       | Archivo de calibración de cámara en formato YAML.                           |
| `qr_dist`          | Distancia real entre los códigos QR en metros.                              |
| `dists_list`       | Lista de distancias (en cm) a usar en cada escena/cuadro.                   |
| `min_mer`          | OPCIONAL. Error mínimo la a hora de buscar mejor versión                    |
| `min_dist`         | OPCIONAL. Valor mínimo de distancia para considerar detecciones válidas.    |
| `min_path`         | OPCIONAL. Ruta mínima para elegir la mejor versión del modelo.              |
| `input_csv_name`   | Nombre del CSV con reproyecciones para generar la nube.                     |

---

## 🖼️ Salidas Generadas

- Imágenes con detecciones superpuestas.
- CSV con coordenadas reproyectadas.
- Nube de puntos 3D en formato `.ply`.

---

> Asegurate de tener tu video en `./input_path/` al igual que los `.csv`, y la calibración en `.input_path/calib`.

---

