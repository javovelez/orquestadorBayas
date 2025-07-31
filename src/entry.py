from lib.opts import opts
import os
import torch
from lib.detectors.circledet_iou import CircledetIOUDetector
import subprocess
import json
import cv2
import numpy as np


def obtener_nombre_sin_extension(ruta_imagen):
  """
  Obtiene el nombre de un archivo sin su extensión a partir de una ruta.

  Args:
    ruta_imagen: La ruta completa al archivo (ej. 'carpeta/subcarpeta/foto_01.png').

  Returns:
    El nombre del archivo sin la extensión (ej. 'foto_01').
  """
  nombre_base = os.path.basename(ruta_imagen)
  nombre_sin_extension = os.path.splitext(nombre_base)[0]
  return nombre_sin_extension

def process_images(opt, image_list, output_folder):

    opt.detector_for_track.pause = False
    flag = True
    dets = dict()
    # rotation = get_video_rotation(opt.demo)
    image_number = 0
    print(f"Procesando video: {opt.demo}")
    
    for img_path in image_list:
      img = cv2.imread(img_path)
      image_name = obtener_nombre_sin_extension(img_path)
      
      os.makedirs(os.path.join(output_folder, 'detector_frames'), exist_ok=True)
      frame_filename = os.path.join(output_folder, 'detector_frames', image_name,'.jpg')
      cv2.imwrite(frame_filename, img)
      
      # cv2.imshow('input', img)
      ret = opt.detector_for_track.run_det_for_byte(img)[1]
      ret = ret.astype(np.float)
      ret = filter(lambda x: x[0]>0 and x[1]>0, ret)
      dets[image_number] = { k:list(r[:4]) for k,r in enumerate(ret)}
      image_number += 1
      print(f'processing image {image_name}')

    json.dump(dets, open(os.path.join(opt.output_folder_json, image_name + '.json'), 'w'))



def get_video_rotation(video_path):
    """Obtiene la rotación del video usando ffprobe (confiable)."""
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream_tags=rotate',
            '-of', 'json',
            video_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        metadata = json.loads(result.stdout)
        rotation = metadata.get('streams', [{}])[0].get('tags', {}).get('rotate', 0)
        return int(rotation) if rotation else 0
    except:
        return 0

def rotate_frame(frame, rotation):
    """Rota el frame según el ángulo especificado."""
    if rotation == 90:
        return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    elif rotation == 180:
        return cv2.rotate(frame, cv2.ROTATE_180)
    elif rotation == 270:
        return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return frame



def encontrar_imagenes_png(directorio):
  """
  Encuentra todas las imágenes .png en un directorio y sus subdirectorios.

  Args:
    directorio: La ruta al directorio que se quiere explorar.

  Returns:
    Una lista con las rutas completas de todas las imágenes .png encontradas.
  """
  lista_imagenes_png = []
  for raiz, _, archivos in os.walk(directorio):
    for nombre_archivo in archivos:
      if nombre_archivo.lower().endswith('.png'):
        lista_imagenes_png.append(os.path.join(raiz, nombre_archivo))
  return lista_imagenes_png

if __name__ == "__main__":

    print(torch.version.cuda)  # Debe coincidir con `nvcc --version`
    print(torch.__version__)
    print(torch.cuda.get_device_name(0))

    torch.backends.cudnn.enabled = False

    Detector = CircledetIOUDetector
    
    args = [
        'cdiou',
        '-if', './images',
        '-of', './output',
        '--load_model', '2022.11.30_grapes_mix_iou.pth'
    ]
        
    opt = opts().init(args)
    
    os.environ['CUDA_VISIBLE_DEVICES'] = opt.gpus_str
    
    opt.detector_for_track = Detector(opt)
    
    image_list = encontrar_imagenes_png('../images')
    
    process_images(opt, image_list, './output')
    
    print("Detección completada") 
