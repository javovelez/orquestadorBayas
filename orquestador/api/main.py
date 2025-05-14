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
        
        '''
        EJECUTAR TAREAS PARA DETECTORBAYAS
        
        Args
        
        - input_folder
        - output_folder
        - video_name
        
        '''
        # detector_bayas_task = celery_app.send_task(
        #     'tasks.detector',
        #     kwargs = {
        #         'input_folder': video_folder,
        #         'output_folder': video_folder,
        #         'video_name': video_name
        #     },
        #     queue='detector_queue'
        # )
        
        # 
        '''
        EJECUTAR TAREAS PARA QR_DETECTOR
        
        Args
        
        - input_folder
        - output_folder
        - video_name
        - modo:str='hibrido'
        - log_file_name:str='qr_detector_log'
        - num_processes:int=None
        - prefijo:str=None
        - qr_det_csv:str='qr_detections.csv'
        - generar_video: bool=True
        - factor_lentitud:float=0.5
        
        '''
        
        log_path = os.path.join(video_folder, 'qr_detector_log.txt')
        
        # 1. Ejecutar frame_ranges y esperar el resultado
        frame_ranges_result = celery_app.send_task(
            'tasks.tasks.qr_detector',
            kwargs={
                'input_folder': video_folder,
                'output_folder': video_folder,
                'video_name': video_name,
                'modo': 'hibrido',
                'log_file_name': 'qr_detector_log',
            },
            queue='qr_detector_queue'
        )

        frame_ranges = frame_ranges_result.get()  # Esperamos los rangos

        # 2. Crear lista de subtareas usando send_task para cada rango
        subtasks = [
            celery_app.signature(
                'tasks.tasks.procesar_frame_range_task',
                kwargs={
                    'video_path': file_path,
                    'log_path': log_path,
                    'start_frame': start,
                    'end_frame': end,
                    'output': video_folder
                },
                queue='qr_detector_queue'
            )
            for start, end in frame_ranges
        ]

        # 3. Crear el group y chain con send_task
        workflow = group(subtasks) | celery_app.signature(
            'tasks.tasks.combinar_resultados',
            queue='qr_detector_queue'
        )

        # 4. Ejecutar la cadena
        result = workflow.apply_async()

        # 5. Obtener resultado final (opcional: bloquear hasta completado)
        datos = result.get()
                
    
    return {"videos": uploaded_videos, "frame_ranges": frame_ranges, "datos": datos}


