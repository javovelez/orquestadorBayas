from fastapi import FastAPI, File, UploadFile
from celery import Celery, chain, group
from typing import List
import os

app = FastAPI()

# Configuración de Celery
celery_app = Celery('orquestador', broker='redis://redis:6379/0', backend='redis://redis:6379/1')

# VIDEOS_PATH = "videos"
SHARED_PATH = "/shared"

@app.post("/upload_videos")
async def upload_videos(videos: List[UploadFile] = File(...)):
    """
    Endpoint to upload videos.
    """
    uploaded_videos = []
    for video in videos:
        
        # Crear carpeta por cada video en SHARED_PATH
        video_name = str(video.filename)
        video_folder = os.path.join(SHARED_PATH, video_name.replace('.mp4', ''))
        os.makedirs(video_folder, exist_ok=True)
        
        # Copiar el video a cada carpeta
        file_path = os.path.join(video_folder, video_name)
        
        with open(file_path, 'wb') as f: 
            f.write(await video.read())

        uploaded_videos.append(video_folder)
        
        # Comenzar ejecución de tareas
        # Asignar ids a tareas videoname+num_tarea (dentro de las funciones)
        pipeline = chain(
            pipeline_detector_bayas(celery_app, video_folder, video_name),
            pipeline_qr_detector(celery_app, video_folder, file_path, video_name)
        )
        
        result = pipeline.apply_async()
        
        # Devolver ids para cada tarea del chain
        
    return {"result": result}

def pipeline_qr_detector(celery_app, video_folder, file_path, video_name):
    
    log_path = os.path.join(video_folder, 'qr_detector_log.txt')
    
    return chain(
        celery_app.signature(
            'tasks.tasks.frame_ranges_task',
            kwargs={
                'input_folder': video_folder,
                'output_folder': video_folder,
                'video_name': video_name,
                'modo': 'hibrido',
                'log_file_name': log_path,
            }, 
        ),
        celery_app.signature(
            'tasks.tasks.generar_tareas_fr_task',
            kwargs={
                'video_path': file_path,
                'log_path': os.path.join(video_folder, 'qr_detector_log.txt'),
                'output': video_folder
            }, 
            queue='qr_detector_queue'
        ),
        celery_app.signature(
            'tasks.tasks.generar_datos_task',
            kwargs={
                'output_folder': video_folder,
            },
            queue='qr_detector_queue'
        )
    )
      
def pipeline_detector_bayas(celery_app, video_folder, video_name):
        
    return celery_app.signature(
        'tasks.detector',
        kwargs = {
            'input_folder': video_folder,
            'output_folder': video_folder,
            'video_name': video_name
        },
        queue='detector_queue'
    )
