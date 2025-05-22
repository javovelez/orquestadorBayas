from src.lib.opts import opts
import os
import torch
from src.lib.detectors.circledet_iou import CircledetIOUDetector
from utils import process_videos

from celery import Celery

NUM_WORKERS = 1

app = Celery('detectorBayas', broker='redis://redis:6379/0', worker_concurrency=NUM_WORKERS, queue='detector_queue')

SHARED_PATH = '/shared'

@app.task
def detector(input_folder, output_folder, video_name):
    
    # Determinar donde guardar el output
    
    torch.backends.cudnn.enabled = False

    Detector = CircledetIOUDetector
    
    args = [
        'cdiou',
        '-if', str(input_folder),
        '-of', str(output_folder),
        '--load_model', '2022.11.30_grapes_mix_iou.pth'
    ]
        
    opt = opts().init(args)
    
    os.environ['CUDA_VISIBLE_DEVICES'] = opt.gpus_str
    
    opt.detector_for_track = Detector(opt)
    opt.demo = os.path.join(input_folder + video_name)
    
    process_videos(opt, video_name)
    
    return {"message": "Detección completada", "video_name": video_name, "output_folder": output_folder}
