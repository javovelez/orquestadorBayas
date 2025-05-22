from celery import Celery
import requests

app = Celery('peticioneshttp', broker='redis://localhost:6379/0', queue='peticiones_queue')

@app.task
def tracker_http_task(_ignore, input_folder, output_folder, video_name, radius, draw_circles, draw_tracking):
    """
    Task to track objects in a video using HTTP request.
    """
    payload = {
        'input_folder': input_folder,
        'output_folder': output_folder,
        'video_name': video_name,
        'radius': radius,
        'draw_circles': draw_circles,
        'draw_tracking': draw_tracking
    }
    
    response = requests.post(
        'http://tracker-service:8000/tracker_task',
        json=payload
    )
    
    response.raise_for_status()
    return response.json()

@app.task
def nubes_http_task(_ignore, 
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
                    num_points: int = 100):
    """
    Task to track objects in a video using HTTP request.
    """
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
    
    response = requests.post(
        'http://nubes-service:8001/nubes',
        json=payload
    )
    
    response.raise_for_status()
    return response.json()