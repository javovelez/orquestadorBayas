from fastapi import FastAPI, File, UploadFile
from celery import Celery, chain, group, chord
from celery.result import AsyncResult
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
        
        # Comenzar ejecución de tareas
        # Asignar ids a tareas videoname+num_tarea (dentro de las funciones)
        
        detector_tasks = pipeline_detector_bayas(celery_app, video_folder, video_name)
        qr_detector_tasks = pipeline_qr_detector(celery_app, video_folder, video_path, video_name)
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
        
        pipeline = qr_detector_tasks | tracker_tasks | nubes_tasks
        
        result = pipeline.apply_async() # Se ejecutan las tareas
        
        task_id = get_task_ids_from_chain(result)
        
        task_id_dict = {
            'video_name': video_name,
            'task_id': task_id,
            'video_folder': video_folder,
        }
        
        tasks_ids.append(task_id_dict)
        
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

def pipeline_qr_detector(celery_app, video_folder, video_path, video_name):
    
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
        queue='qr_detector_queue',
        task_id=f'{video_name}_frame_ranges_task'
    )
    
    # Genera subtareas paralelas para procesar rangos de frames, combina resultados, y genera datos
    generar_datos_task = celery_app.signature(
        'tasks.tasks.generar_tareas_fr_task',
        kwargs={
            'video_path': video_path,
            'log_path': os.path.join(video_folder, 'qr_detector_log.txt'),
            'output_folder': video_folder
        }, 
        queue='qr_detector_queue',
        task_id=f'{video_name}_generar_datos_qr_task'
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
        queue='detector_queue',
        task_id=f'{video_name}_detector_task'
    )

def pipeline_tracker(celery_app, video_folder, radius, video_name, draw_circles, draw_tracking):
    
    return celery_app.signature(
        'tasks.tracker_http_task',
        kwargs = {
            'input_folder': video_folder,
            'output_folder': video_folder,
            'video_name': video_name,
            'radius': radius,
            'draw_circles': draw_circles,
            'draw_tracking': draw_tracking
        },
        queue='peticiones_queue',
        task_id=f'{video_name}_tracker_task'
    )
    
def pipeline_nubes(celery_app, 
                   input_folder, 
                   output_folder, 
                   video_name, 
                   baya_thresh,
                   qr_thresh,
                   cant_nubes,
                   calib_file,
                   qr_dist,
                   dists_list,
                   reproy_csv_name, 
                   num_points): 
    
    return celery_app.signature(
        'tasks.nubes_http_task',
        kwargs = {
            'input_folder': input_folder,
            'output_folder': output_folder,
            'video_name': video_name,
            'baya_thresh': baya_thresh,
            'qr_thres': qr_thresh,
            'qr_dist': qr_dist,
            'cant_nubes': cant_nubes,
            'calib_file': calib_file,
            'dists_list': dists_list,
            'reproy_csv_name': reproy_csv_name,
            'num_points': num_points
        },
        queue='peticiones_queue',
        task_id=f'{video_name}_nubes_task'
    )
