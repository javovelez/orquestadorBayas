"""
Módulo principal para la detección y procesamiento de códigos QR en videos.

Este módulo utiliza Celery para distribuir tareas de procesamiento de video,
detección de QR y generación de informes y visualizaciones.
"""

from src.utils import generar_csv, generar_video_con_qr
from src.reporting import generar_informe, generar_grafico_distribucion, generar_grafico_temporal
from tasks.hybrid_processing_tasks import procesar_video_parallel

import cv2
import numpy as np
import os
from pyzbar.pyzbar import decode

from celery import Celery, shared_task, group, signature, chord, chain

# Configuración de workers
NUM_WORKERS = 4

# Configuración de Celery
app = Celery(
    'qrDetector',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/1',
    worker_concurrency=NUM_WORKERS,
    queue='qr_detector_queue'
)

@app.task
def frame_ranges_task(input_folder, output_folder, video_name, modo: str = 'hibrido',
                     log_file_name: str = 'qr_detector_log', num_processes: int = 4):
    """
    Divide el video en rangos de frames para procesamiento paralelo.

    Args:
        input_folder (str): Directorio de entrada donde se encuentra el video.
        output_folder (str): Directorio de salida para los resultados.
        video_name (str): Nombre del archivo de video a procesar.
        modo (str, optional): Modo de procesamiento. Defaults to 'hibrido'.
        log_file_name (str, optional): Nombre del archivo de log. Defaults to 'qr_detector_log'.
        num_processes (int, optional): Número de procesos a usar. Defaults to 4.

    Returns:
        list: Lista de tuplas con los rangos de frames.

    Raises:
        ValueError: Si el modo de procesamiento no es válido.
    """
    video_path = os.path.join(input_folder, video_name+'.mp4')
    log_file_path = os.path.join(output_folder, log_file_name)

    if modo:
        frame_ranges = procesar_video_parallel(video_path, log_file_path, output_folder, num_processes)
    else:
        raise ValueError("Modo de procesamiento no válido")

    return frame_ranges


@app.task
def generar_tareas_fr_task(frame_ranges, video_path: str, log_path: str, output_folder: str):
    """
    Genera tareas Celery para cada rango de frames.

    Args:
        frame_ranges (list): Lista de rangos de frames a procesar.
        video_path (str): Ruta al archivo de video.
        log_path (str): Ruta al archivo de log.
        output_folder (str): Ruta de salida para los resultados.

    Returns:
        AsyncResult: Resultado asíncrono del chord de tareas.
    """
    subtasks = [
        signature(
            'tasks.tasks.procesar_frame_range_task',
            kwargs={
                'video_path': video_path,
                'log_path': log_path,
                'start_frame': start,
                'end_frame': end,
                'output_folder': output_folder
            },
            queue='qr_detector_queue'
        )
        for start, end in frame_ranges
    ]
    
    workflow = (
        group(subtasks) |
        signature('tasks.tasks.combinar_resultados_task', queue='qr_detector_queue') |
        signature('tasks.tasks.generar_datos_task', kwargs={'output_folder': output_folder}, queue='qr_detector_queue')
    )

    result = workflow.apply_async()
    return result.id


@app.task
def procesar_frame_range_task(video_path: str, log_path: str, start_frame: int, end_frame: int,
                            output_folder: str, borde: int = 15, tamano_parche: int = 300):
    """
    Procesa un rango específico de frames para detectar códigos QR.

    Args:
        video_path (str): Ruta al archivo de video.
        log_path (str): Ruta al archivo de log.
        start_frame (int): Frame inicial del rango.
        end_frame (int): Frame final del rango.
        output_folder (str): Directorio de salida para los resultados.
        borde (int, optional): Borde adicional alrededor del QR. Defaults to 15.
        tamano_parche (int, optional): Tamaño de los parches para dividir el frame. Defaults to 300.

    Returns:
        list: Lista de diccionarios con información de los QRs detectados.
    """
    datos = []
    os.makedirs(f'{output_folder}/qr_frames/', exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    frame_num = 0

    while frame_num < end_frame and cap.isOpened():
        ret, frame = cap.read()

        if frame_num < start_frame:
            frame_num += 1
            continue

        if not ret:
            print(f"Error al leer el frame {frame_num}.")
            frame_num += 1
            continue

        try:
            height, width, _ = frame.shape
            for y in range(0, height, tamano_parche):
                for x in range(0, width, tamano_parche):
                    x_end = min(x + tamano_parche, width)
                    y_end = min(y + tamano_parche, height)
                    parche = frame[y:y_end, x:x_end]
                    qrs = decode(parche)

                    for qr in qrs:
                        (px, py, pw, ph) = qr.rect
                        x_start = max(0, x + px - borde)
                        y_start = max(0, y + py - borde)
                        x_final = min(width, x + px + pw + borde)
                        y_final = min(height, y + py + ph + borde)
                        qr_region = frame[y_start:y_final, x_start:x_final].copy()
                        data = qr.data.decode('utf-8')

                        qr_detector = cv2.QRCodeDetector()
                        retval, points = qr_detector.detect(qr_region)

                        if retval and points is not None:
                            points = points[0]
                            if es_rectangulo_valido(points):
                                puntos_qr = [(int(point[0]) + x_start, int(point[1]) + y_start) for point in points]

                                for punto in puntos_qr:
                                    cv2.circle(frame, punto, radius=5, color=(0, 0, 255), thickness=-1)
                                cv2.putText(frame, data, (puntos_qr[0][0] - 10, puntos_qr[0][1] - 10),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

                                datos.append({
                                    'frame': frame_num,
                                    'data': data,
                                    'x1': puntos_qr[0][0], 'y1': puntos_qr[0][1],
                                    'x2': puntos_qr[1][0], 'y2': puntos_qr[1][1],
                                    'x3': puntos_qr[2][0], 'y3': puntos_qr[2][1],
                                    'x4': puntos_qr[3][0], 'y4': puntos_qr[3][1],
                                    'detected_by': 'opencv'
                                })

        except Exception as e:
            with open(log_path, 'a') as log_file:
                log_file.write(f'Error en el frame {frame_num}: {str(e)}\n')

        cv2.imwrite(f'{output_folder}/qr_frames/frame_completo_{frame_num}.png', frame)
        frame_num += 1

    cap.release()
    return datos


@app.task
def combinar_resultados_task(results):
    """
    Combina los resultados de todas las tareas de procesamiento de frames.

    Args:
        results (list): Lista de listas con resultados de detección.

    Returns:
        list: Lista combinada de todos los resultados.
    """
    
    print("Combinando resultados de todas las tareas...")
    
    return [item for sublist in results for item in sublist]


@shared_task
def es_rectangulo_valido(points):
    """
    Verifica si los puntos forman un cuadrilátero válido.

    Args:
        points (list): Lista de puntos con coordenadas (x, y).

    Returns:
        bool: True si los puntos forman un cuadrilátero válido, False en caso contrario.
    """
    pts = np.array(points, np.int32)

    def calcular_vector(p1, p2):
        return np.array([p2[0] - p1[0], p2[1] - p1[1]])

    v1 = calcular_vector(pts[0], pts[1])
    v2 = calcular_vector(pts[1], pts[2])
    v3 = calcular_vector(pts[3], pts[2])
    v4 = calcular_vector(pts[0], pts[3])

    def calcular_angulo_entre_vectores(v1, v2):
        cos_theta = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        angulo = np.arccos(np.clip(cos_theta, -1.0, 1.0))
        return np.degrees(angulo)

    angulo_opuesto1 = calcular_angulo_entre_vectores(v1, v3)
    angulo_opuesto2 = calcular_angulo_entre_vectores(v2, v4)

    umbral = 10
    if abs(angulo_opuesto1) > umbral or abs(angulo_opuesto2) > umbral:
        return False

    return True


@app.task
def generar_datos_task(datos, output_folder, prefijo: str = None, qr_det_csv: str = 'qr_detections.csv',
                      generar_video: bool = True, factor_lentitud: float = 0.5):
    """
    Genera archivos de salida con los resultados de la detección.

    Args:
        datos (list): Datos de detección de QRs.
        output_folder (str): Directorio de salida.
        prefijo (str, optional): Prefijo para los archivos. Defaults to None.
        qr_det_csv (str, optional): Nombre del archivo CSV. Defaults to 'qr_detections.csv'.
        generar_video (bool, optional): Si generar video con resultados. Defaults to True.
        factor_lentitud (float, optional): Factor de velocidad del video. Defaults to 0.5.

    Returns:
        dict: Diccionario con rutas de los archivos generados.
    """
    
    print("Generando archivos de salida...")
    
    if datos is None:
        raise ValueError("No se han recibido datos en generar_datos_task.")
    
    video_path = os.path.join(output_folder)
    qr_detections_path = os.path.join(output_folder, qr_det_csv)
    qr_temporal_file = os.path.join(output_folder, 'qr_temporal_graph.png')
    qr_distribution_file = os.path.join(output_folder, 'qr_temporal_dist.png')
    output_video_file = os.path.join(output_folder, 'qr_detections_video.mp4')

    generar_csv(datos, prefijo, qr_detections_path)
    generar_informe(datos)
    generar_grafico_temporal(datos, qr_temporal_file)
    generar_grafico_distribucion(datos, qr_distribution_file)

    if generar_video:
        print("Generando el video con los recuadros de los códigos QR detectados...")
        generar_video_con_qr(video_path, datos, output_video_file, factor_lentitud)

    