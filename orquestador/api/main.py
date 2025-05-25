from fastapi import FastAPI, File, UploadFile, HTTPException
from celery import Celery, chain, group, chord
from celery.result import AsyncResult
from pipelines import pipeline_detector_bayas, pipeline_qr_detector, pipeline_tracker, pipeline_nubes
from typing import List, Dict, Any
import os
import requests

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
    
    # Todo esto va a tener que estar en la petición
    num_processes = 4
    generar_video_qr = True
    factor_lentitud = 0.5
    baya_thresh = 0.7*150, 
    qr_thresh = 120, 
    cant_nubes = 1, 
    calib_file = 'MotorolaG200_Javo_Vertical.yaml', 
    qr_dist = 2.1, 
    dists_list = [10, 40, 5], 
    reproy_csv_name = 'reproyecciones.csv',
    num_points = 100
    
    uploaded_videos = []
    tasks_ids = []
    for video in videos:
        
        # Crear carpeta por cada video en SHARED_PATH
        video_name = str(video.filename).replace('.mp4', '')
        video_folder = os.path.join(SHARED_PATH, video_name)
        os.makedirs(video_folder, exist_ok=True)
        
        # Copiar el video a cada carpeta
        video_path = os.path.join(video_folder, video_name + '.mp4')
        
        with open(video_path, 'wb') as f: 
            f.write(await video.read())

        uploaded_videos.append(video_folder)
        
        # Ejecución de tareas 
        
        detector_tasks = pipeline_detector_bayas(celery_app, video_folder, video_name)
        qr_detector_tasks = pipeline_qr_detector(celery_app, video_folder, video_name, num_processes, generar_video_qr, factor_lentitud)
        tracker_tasks = pipeline_tracker(celery_app, video_folder=video_folder, radius=10, video_name=video_name, draw_circles=True, draw_tracking=True)
        nubes_tasks = pipeline_nubes(celery_app, 
                                     video_folder, 
                                     video_folder, 
                                     video_name,
                                     baya_thresh, 
                                     qr_thresh, 
                                     cant_nubes, 
                                     calib_file, 
                                     qr_dist, 
                                     dists_list, 
                                     reproy_csv_name, 
                                     num_points)
        
        print(qr_detector_tasks, tracker_tasks)
        
        pipeline = chain(detector_tasks, qr_detector_tasks, tracker_tasks, nubes_tasks)
        
        result = pipeline.apply_async() # Se ejecutan las tareas
        
        task_id = get_task_ids_from_chain(result)
        
        task_id_dict = {
            'video_name': video_name,
            'task_id': task_id,
            'video_folder': video_folder,
        }
        
        tasks_ids.append(task_id_dict)
        
    return tasks_ids

@app.get("/task_status/{task_id}")
def task_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    if not result:
        raise HTTPException(status_code=404, detail="Task ID no encontrado")
    return {
        "task_id": task_id,
        "state": result.state,
        "result": result.result,
        "info": result.info
    }

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