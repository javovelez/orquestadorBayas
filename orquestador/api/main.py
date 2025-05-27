from fastapi import FastAPI, File, UploadFile
from celery import chain, group
from .tasks import detector_http_task, qr_detector_http_task, tracker_http_task, nubes_http_task
from typing import List, Dict, Any
import os
import shutil

app = FastAPI()
SHARED_PATH = "/shared"

@app.post("/upload_videos")
async def upload_videos(videos: List[UploadFile] = File(...)):
    """Endpoint que recibe videos y lanza pipelines en paralelo."""

    # TODO ESTO VA EN LA REQUEST
    num_processes = 4
    generar_video_qr = True
    factor_lentitud = 0.5
    baya_thresh = 0.7*150
    qr_thresh = 120
    cant_nubes = 1 
    calib_file = 'MotorolaG200_Javo_Vertical.yaml'
    qr_dist = 2.1
    dists_list = [10, 40, 5], 
    reproy_csv_name = 'reproyecciones.csv'
    num_points = 100

    # Procesar videos en lotes de 4
    all_task = []
    all_task_ids = [] 
    uploaded_videos = []
    for video in videos:
        
        # Crear carpeta por cada video en SHARED_PATH
        video_name = str(video.filename).replace('.mp4', '')
        video_folder = os.path.join(SHARED_PATH, video_name)
        os.makedirs(video_folder, exist_ok=True)
        video_path = os.path.join(video_folder, video_name + '.mp4')
        
        try:
            with open(video_path, 'wb') as f:
                shutil.copyfileobj(video.file, f)
                print(f"Video guardado en: {video_path}")
        except Exception as e:
            return {"error": f"Error al guardar el video: {str(e)}"}
        
        uploaded_videos.append(video_folder)

        # Crear un grupo de pipelines (cada pipeline es una cadena)
        # CAMBIAR POR PARAMETROS COMO ANTES
        pipeline = chain(
            detector_http_task.s(video_folder, video_folder, video_name)
            # qr_detector_http_task.s(video_folder, video_folder, video_name, num_processes, generar_video_qr, factor_lentitud),
            # tracker_http_task.s(video_folder, video_folder, video_name, radius=10, draw_circles=True, draw_tracking=True),
            # nubes_http_task.s(video_folder, video_folder, video_name, baya_thresh, qr_thresh, cant_nubes, calib_file, qr_dist, dists_list, reproy_csv_name, num_points)
        )

        all_task.append(pipeline)
    
    # Ejecutar el grupo en paralelo
    pipeline = group(all_task)
    group_result = pipeline.apply_async()
    all_task_ids.extend([task.id for task in group_result.results])  # Guardar IDs de tareas

    return {"task_ids": upload_videos}