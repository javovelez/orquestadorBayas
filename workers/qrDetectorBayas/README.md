# EN PROCESO DE AJUSTES
Debo hacer varias mejoras en cuanto a petición (no pedir el output del video por ejemplo, lo mismo con el input de video) WIP!!. Considerar que fue el primer contenedor desarrollado y estaba verde.

## Cómo usar? (por ahora) 
Hacer una petición de la forma al endpoint `localhost/qr_detector` en POST (no es POST, a arreglar)
```
{
  "video_path": "input/video.mp4",
  "salida_csv": "datos.csv",
  "output_path": "output/",
  "output_video": "output_video.mp4",
  "log_path": "log.txt",
  "num_processes": 4,
  "generar_video": true,
  "modo": "hibrido"
}
```

