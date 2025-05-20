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