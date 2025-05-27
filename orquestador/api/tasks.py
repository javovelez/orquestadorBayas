from .celery_app import celery_app
import httpx
from typing import Any, Dict

@celery_app.task
def detector_http_task(input_folder: str, output_folder: str, video_name: str) -> Dict[str, Any]:
    """Tarea asíncrona para el detector de bayas usando HTTPX"""
    payload = {
        'input_folder': input_folder,
        'output_folder': output_folder,
        'video_name': video_name    
    }
    
    with httpx.Client(timeout=None) as client:
        response = client.post(
            'http://detector-service:8001/detector_task',
            json=payload
        )
        response.raise_for_status()
        return response.json()

@celery_app.task
def qr_detector_http_task(
    _ignore: Any,
    input_folder: str,
    output_folder: str,
    video_name: str,
    num_processes: int,
    generar_video: bool,
    factor_lentitud: float
) -> Dict[str, Any]:
    """Tarea asíncrona para el detector QR usando HTTPX"""
    payload = {
        'input_folder': input_folder,
        'output_folder': output_folder,
        'video_name': video_name,
        'num_processes': num_processes,
        'generar_video': generar_video,
        'factor_lentitud': factor_lentitud       
    }
    
    with httpx.Client(timeout=None) as client:
        response = client.post(
            'http://qrdetector-service:8002/qr_detector_task',
            json=payload
        )
        response.raise_for_status()
        return response.json()

@celery_app.task
def tracker_http_task(
    _ignore: Any,
    input_folder: str,
    output_folder: str,
    video_name: str,
    radius: int,
    draw_circles: bool,
    draw_tracking: bool
) -> Dict[str, Any]:
    """Tarea asíncrona para el tracker usando HTTPX"""
    payload = {
        'input_folder': input_folder,
        'output_folder': output_folder,
        'video_name': video_name,
        'radius': radius,
        'draw_circles': draw_circles,
        'draw_tracking': draw_tracking
    }
    
    with httpx.Client(timeout=None) as client:
        response = client.post(
            'http://tracker-service:8003/tracker_task',
            json=payload
        )
        response.raise_for_status()
        return response.json()

@celery_app.task
def nubes_http_task(
    _ignore: Any,
    input_folder: str, 
    output_folder: str, 
    video_name: str, 
    baya_thresh: float = 0.7*150, 
    qr_thresh: float = 120, 
    cant_nubes: int = 1, 
    calib_file: str = 'MotorolaG200_Javo_Vertical.yaml', 
    qr_dist: float = 2.1, 
    dists_list: list = [10, 40, 5], 
    reproy_csv_name: str = 'reproyecciones.csv',
    num_points: int = 100
) -> Dict[str, Any]:
    """Tarea asíncrona para el procesamiento de nubes usando HTTPX"""
    payload = {
        'input_folder': input_folder,
        'output_folder': output_folder,
        'video_name': video_name,
        'baya_threshold': baya_thresh,
        'qr_threshold': qr_thresh,
        'qr_dist': qr_dist,
        'cantidad_nubes': cant_nubes,
        'calib_file': calib_file,
        'dists_list': dists_list,
        'reproy_csv_name': reproy_csv_name,
        'num_points': num_points
    }
    
    with httpx.Client(timeout=None) as client:
        response = client.post(
            'http://nubes-service:8004/nubes_task',
            json=payload
        )
        response.raise_for_status()
        return response.json()