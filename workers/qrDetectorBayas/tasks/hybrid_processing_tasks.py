import shutil
import cv2
import numpy as np
import os
from pyzbar.pyzbar import decode
from multiprocessing import Pool

from celery import Celery, shared_task, group

@shared_task
def procesar_video_parallel(video_path: str, log_path: str, output_path: str, num_processes: int = 4, borde: int = 15):
    """
    Procesa un video en paralelo utilizando múltiples procesos para detectar códigos QR de manera híbrida.

    Args:
        video_path (str): Ruta al archivo de video.
        log_path (str): Ruta al archivo de log para registrar errores.
        num_processes (int): Número de procesos a utilizar para la ejecución paralela.
        borde (int): Tamaño del borde adicional para el recorte del área del QR (valor por defecto 15).

    Returns:
        list: Lista de diccionarios con información sobre los códigos QR detectados.
    """
    # Borrar la carpeta 'regiones' si existe y crearla de nuevo
    if os.path.exists('regiones'):
        shutil.rmtree('regiones')
    os.makedirs('regiones')

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    # Dividir el trabajo en frames
    frame_ranges = [(i * (total_frames // num_processes), (i + 1) * (total_frames // num_processes)) for i in range(num_processes)]    
    frame_ranges[-1] = (frame_ranges[-1][0], total_frames)  # Asegurarse de que el último proceso llegue hasta el final
    
    return frame_ranges
