from fastapi import FastAPI, File, UploadFile
from celery import Celery
from typing import List
import os

app = FastAPI()

# Configuración de Celery
celery_app = Celery('orquestador', broker='redis://redis:6379/0')

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

        uploaded_videos.append(video_folder)\
        
        # Ejecuto tarea para detectorBayas
        detector_bayas_task = celery_app.send_task(
            'tasks.detector',
            kwargs = {
                'input_folder': video_folder,
                'output_folder': video_folder,
                'video_name': video_name
            } 
        )

    return {"videos": uploaded_videos}


