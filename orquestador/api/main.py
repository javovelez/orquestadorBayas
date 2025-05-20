from fastapi import FastAPI, File, UploadFile
from celery import Celery, chain, group, chord
from celery.result import AsyncResult
from typing import List, Dict, Any
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
        
        detector_tasks = pipeline_detector_bayas(celery_app, video_folder, video_name)
        qr_detector_tasks = pipeline_qr_detector(celery_app, video_folder, file_path, video_name)
        tracker_tasks = pipeline_tracker(celery_app, video_folder=video_folder, radius=10, video_name=video_name, draw_circles=True, draw_tracking=True)
        
        pipeline = chain(
            # detector_tasks,
            qr_detector_tasks,
            tracker_tasks
        )
        result = pipeline.apply_async()
        
        tasks_ids = get_task_ids_from_chain(result)
        
        tasks_ids = {
            'video_folder': video_folder,
            'video_name': video_name,
            'tasks_ids': tasks_ids
        }
        
    return tasks_ids

def get_task_ids_from_chain(chain_result: AsyncResult) -> Dict[str, str]:
    """
    Recursively extracts task IDs from a Celery chain result.
    
    Args:
        chain_result: The AsyncResult of the chain
        
    Returns:
        Dict containing all task IDs in the chain
    """
    task_ids = {}
    current = chain_result
    
    # The chain is stored in the result's 'parent' attribute
    while hasattr(current, 'parent') and current.parent:
        task_ids[current.id] = {
            'task_name': current.name,
            'state': current.state
        }
        current = current.parent
    
    # Add the last task in the chain
    if current:
        task_ids[current.id] = {
            'task_name': current.name,
            'state': current.state
        }
    
    return task_ids

def pipeline_qr_detector(celery_app, video_folder, file_path, video_name):
    
    log_path = os.path.join(video_folder, 'qr_detector_log.txt')
    
    # Genera la lista con rango de frames: frame ranges
    frame_ranges_task = celery_app.signature(
        'tasks.tasks.frame_ranges_task',
        kwargs={
            'input_folder': video_folder,
            'output_folder': video_folder,
            'video_name': video_name,
            'modo': 'hibrido',
            'log_file_name': log_path,
        }, 
        queue='qr_detector_queue'
    )
    
    # Genera subtareas paralelas para procesar rangos de frames, combina resultados, y genera datos
    generar_datos_task = celery_app.signature(
        'tasks.tasks.generar_tareas_fr_task',
        kwargs={
            'video_path': file_path,
            'log_path': os.path.join(video_folder, 'qr_detector_log.txt'),
            'output_folder': video_folder
        }, 
        queue='qr_detector_queue'
    )
    
    return chain(
        frame_ranges_task,
        generar_datos_task
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

def pipeline_tracker(celery_app, video_folder, radius, video_name, draw_circles, draw_tracking):
    
    return celery_app.signature(
        'tasks.tracker_task',
        kwargs = {
            'input_folder': video_folder,
            'output_folder': video_folder,
            'video_name': video_name,
            'radius': radius,
            'draw_circles': draw_circles,
            'draw_tracking': draw_tracking
        },
        queue='tracker_queue'
    )