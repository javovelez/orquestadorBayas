from fastapi import FastAPI, HTTPException, Path
from .schemas import ProcesarVideoRequest
import subprocess
from .qr_processing import procesar_video_parallel
from .utils import generar_csv, generar_video_con_qr
from .reporting import generar_informe, generar_grafico_temporal, generar_grafico_distribucion

import sys
import os

print("Python ejecutado:", sys.executable)
print("Directorio actual:", os.getcwd())
print("Archivos en el directorio actual:", os.listdir("."))

app = FastAPI()

@app.post("/qr_detector_task")
async def procesar_video(request: ProcesarVideoRequest):
    
    video_name = request.video_name
    video_folder = request.input_folder
    video_path = os.path.join(video_folder, video_name + '.mp4')
    output_folder = request.output_folder
    output_video = os.path.join(output_folder, video_name + '_qr_det_video.mp4')
    log_path = os.path.join(output_folder, 'detections_log.txt')
    num_processes = request.num_processes
    generar_video = request.generar_video
    factor_lentitud = request.factor_lentitud
    qr_detections_csv = os.path.join(output_folder, 'qr_detections.csv')
    qr_temporal_graph = os.path.join(output_folder, 'qr_temporal_graph.png')
    qr_distribution_graph = os.path.join(output_folder, 'qr_distribution_graph.png')

    try:
        # Procesar el video y generar CSV
        datos = procesar_video_parallel(video_path, log_path, output_folder, num_processes)

        generar_csv(datos, video_name, qr_detections_csv)

        # Generar informe y gráficos
        generar_informe(datos)
        generar_grafico_temporal(datos, qr_temporal_graph)
        generar_grafico_distribucion(datos, qr_distribution_graph)

        # Si se indica, generar el video con los recuadros de los códigos QR detectados
        if generar_video:
            print("Generando el video con los recuadros de los códigos QR detectados...")
            generar_video_con_qr(video_path, datos, output_video, factor_lentitud)
        
        result = {
            'output_video': output_video,
            'log_path': log_path,
            'qr_detections_csv': qr_detections_csv,
            'qr_temporal_graph': qr_temporal_graph,
            'qr_distribution_graph': qr_distribution_graph
        }
        
        return result
        
    except subprocess.CalledProcessError as e:
        
        detalles = {
            "error": "error con QR Detector",
            "command": e.args,
            "exit_code": e.returncode, 
            "stdout": e.stdout,
            "stderr": e.stderr
        }

        raise HTTPException(status_code=400, detail=detalles)