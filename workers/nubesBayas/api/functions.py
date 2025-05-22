from concurrent.futures import ProcessPoolExecutor, as_completed
import cv2
import os
import subprocess
from pathlib import Path
import pandas as pd
import argparse
import open3d as o3d
import numpy as np
import glob

# Pasar video.mp4 a frames
def video_to_frame(video_path, output_folder, video_name="VID_UNKNOWN"):

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: No se pudo abrir el video")
        print(video_path)

    frame_count = 0
    # Temporal
    racimo_id = "001"

    print(f"Extrayendo frames de {video_path} y guardando en {output_folder}...")

    while True:
        # Leer el siguiente frame
        ret, frame = cap.read()
        
        # Si no hay más frames, salir del bucle
        if not ret:
            break
        
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        # Guardar el frame como imagen
        frame_filename = os.path.join(output_folder, f"{racimo_id}_{video_name}_{frame_count}.png")
        cv2.imwrite(frame_filename, frame)

        frame_count += 1

    # Liberar el objeto VideoCapture
    cap.release()
    # Cerrar todas las ventanas de OpenCV
    cv2.destroyAllWindows()
    
    print(f"Se han extraído {frame_count} frames y se han guardado en {output_folder}.")

# Obtener MER
def read_and_process_csv(csv_file_path):
    if not os.path.exists(csv_file_path):
        print(f"El archivo {csv_file_path} no existe.")
        return None
    df = pd.read_csv(csv_file_path)
    df = df[df['label'] == 'baya']
    #drop_column = 'Unnamed: 13'
    #df = df.drop(drop_column, axis=1)

    # Filtrando las filas con algún valor nulo
    df = df.dropna(subset=["error"])
    
    video_name = list(df['img_name'])[0]
    video_name = video_name.rsplit('_', 1)[0]
    
    r_median = df.groupby('frame_id')['r'].median()
    df['r_median'] = df['frame_id'].map(r_median)
    
    # print(df[df['r_median'] == 0])
    # print(df.loc[df['r_median'] == 0, 'frame_id'].unique())
    
    df['error_ratio'] = df['error'] / df['r_median']    # Esto queda de antes

    if (df['r_median'] == 0).any():
        print("Advertencia: Hay valores 0 en 'r_median', lo que causará divisiones infinitas.")
        
    # Obtener la suma de 'error_ratio' en todo el DataFrame
    suma_error_ratio = df['error_ratio'].sum()

    # Obtener la media de 'error_ratio' en todo el DataFrame
    media_error_ratio = df['error_ratio'].mean()

    parent , _ = os.path.split(csv_file_path)
    _ , init_frames = os.path.split(parent)

    return media_error_ratio

# Generar triangulación
def triangulacion(calib_path, bundles_path, frames_path, output_path, qr_dist, dist, input_csv_name):
    try: 
        
        print(f"[{dist}] Iniciando triangulación... \n") 
        
        command = [
            "./Release/triangulacionDeBayas",
            "-c", calib_path,
            "-d", bundles_path,
            "-x", str(qr_dist),     # QR dist
            "-i", str(frames_path),
            "-o", str(output_path),
            "--init_distance", dist
        ]

        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        repro_path = glob.glob(f"{output_path}/{dist}_*/{input_csv_name}")
            
        if repro_path:
            # print(f"Ruta encontrada: {repro_path[0]}")
            repro_path = repro_path[0]
        else:
            print(f"No se encontró el archivo reproyeccion.csv en una carpeta que empiece con '{dist}_'")
            return None
                
        media_error_ratio = read_and_process_csv(repro_path)
        
        return {
            "repro_path": repro_path,
            "media_error_ratio": media_error_ratio,
            "dist": dist
        }
        
    except subprocess.CalledProcessError as e:
        print(f"[{dist}] Error en la triangulación: {e.stderr}")  
        return None
    
# Generar y obtener la mejor triangulación
def get_best_triangulacion(output_path:str, dists_list:list, min_mer:int=10, min_dist:int=0, min_path:str='', input_csv_name:str='Reproyecciones.csv', calib_path='', bundles_path='', frames_path='', qr_dist:float=2.1, max_workers:int = 6):
    mer_minimo = min_mer
    dist_minimo = min_dist
    path_minimo = min_path
     
    dists = [str(i) for i in range(dists_list[0], dists_list[1], dists_list[2])]
    results = []
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        
        # Ejecuto la triangulación en paralelo
        futures = {
            executor.submit(triangulacion, calib_path, bundles_path, frames_path, output_path, qr_dist, dist, input_csv_name): dist for dist in dists
        }
        
        best = None
        
        # Guardo resultados de ejecución
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
                
                if best is None or result['media_error_ratio'] < mer_minimo:
                    best = result
                    mer_minimo = result['media_error_ratio']
                    dist_minimo = result['dist']
                    path_minimo = result['repro_path']
                    print(f"Mejor reconstrucción hasta ahora: {mer_minimo} con distancia {dist_minimo}")

                if mer_minimo < 0.08:
                    print(f"Esta reconstrucción es lo suficientemente buena porque su mer es de {result['media_error_ratio']}")
                    break
                
    # Guardar resultados de las triangulaciones
    logs = pd.DataFrame(results)
    logs.to_csv(os.path.join(output_path, 'logs.csv'), index=False)
            
    return path_minimo, mer_minimo, dist_minimo




# Generar nube densa
def generate_random_points_on_sphere(center, radius, num_points):
    """Genera puntos aleatorios en la superficie de una esfera con radio dado."""
    phi = np.random.uniform(0, 2 * np.pi, num_points)
    costheta = np.random.uniform(-1, 1, num_points)
    theta = np.arccos(costheta)

    x = center[0] + radius * np.sin(theta) * np.cos(phi)
    y = center[1] + radius * np.sin(theta) * np.sin(phi)
    z = center[2] + radius * costheta

    return np.column_stack((x, y, z))


def csv_to_ply_with_sphere(csv_file, ply_file, num_points):    
    df = pd.read_csv(csv_file)

    # Filtrar solo las filas con label == 'baya'
    df_bayas = df[df['label'] == 'baya']
    
    if not {'X', 'Y', 'Z', 'R3D'}.issubset(df.columns):
        raise ValueError("El CSV debe contener las columnas 'X', 'Y', 'Z', 'R3D', y 'label'")
    
    puntos_totales = []

    # Generar puntos aleatorios en la esfera para cada baya
    for _, row in df_bayas.iterrows():
        centro = (row['X'], row['Y'], row['Z'])
        radio = row['R3D']
        puntos = generate_random_points_on_sphere(centro, radio, num_points)
        puntos_totales.append(puntos)
    
    # Convertir lista a un solo array
    puntos_totales = np.vstack(puntos_totales)

    # Guardar como archivo PLY
    with open(ply_file, 'w') as f:
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write(f"element vertex {len(puntos_totales)}\n")
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")
        f.write("end_header\n")
        
        for punto in puntos_totales:
            f.write(f"{punto[0]} {punto[1]} {punto[2]}\n")

def visualizar_ply(ply_file):
    """Carga y visualiza un archivo PLY en una ventana interactiva."""
    nube = o3d.io.read_point_cloud(ply_file)
    o3d.visualization.draw_geometries([nube])


# PRUEBA GBT - IGNORAR
def get_best_triangulacion2(output_path:str, dists_list:list, min_mer:int=10, min_dist:int=0, min_path:str='', input_csv_name:str='Reproyecciones.csv'):
    mer_minimo = min_mer
    dist_minimo = min_dist
    path_minimo = min_path
    
    dists = [str(i) for i in range(dists_list[0], dists_list[1], dists_list[2])]
    
    for dist in dists:
        
        print(dist)
        
        repro_path = glob.glob(f"{output_path}/{dist}_*/{input_csv_name}")
        
        if repro_path:
            print(f"Ruta encontrada: {repro_path[0]}")
            repro_path = repro_path[0]
        else:
            print(f"No se encontró el archivo reproyeccion.csv en una carpeta que empiece con '{dist}_'")
            continue
            
        media_error_ratio = read_and_process_csv(repro_path)
                
        if media_error_ratio < 0.08:
            print(f"Esta reconstrucción es lo suficientemente buena porque su mer es de {media_error_ratio}")
            return repro_path, media_error_ratio, dist
        
        if media_error_ratio < mer_minimo:
            mer_minimo = media_error_ratio
            dist_minimo = dist
            path_minimo = repro_path
                    
    return path_minimo, mer_minimo, dist_minimo
