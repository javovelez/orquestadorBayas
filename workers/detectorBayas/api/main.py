from fastapi import FastAPI
from .schemas import DetectorRequest
from src.lib.opts import opts
import os
import torch
from src.lib.detectors.circledet_iou import CircledetIOUDetector
from .utils import process_videos
import torch

app = FastAPI()

print(torch.version.cuda)  # Debe coincidir con `nvcc --version`
print(torch.__version__)

@app.post("/detector_task")
async def detector(request: DetectorRequest):
    
    print(torch.__version__)
    print(torch.version.cuda)
    print(torch.cuda.get_device_name(0))

    torch.backends.cudnn.enabled = False

    Detector = CircledetIOUDetector
    
    args = [
        'cdiou',
        '-if', str(request.input_folder),
        '-of', os.path.join(request.output_folder),
        '--load_model', '2022.11.30_grapes_mix_iou.pth'
    ]
        
    opt = opts().init(args)
    
    os.environ['CUDA_VISIBLE_DEVICES'] = opt.gpus_str
    
    opt.detector_for_track = Detector(opt)
    opt.demo = os.path.join(request.input_folder, request.video_name + '.mp4')
    
    print(f"Procesando video: {opt.demo}")
    
    process_videos(opt, video_name=request.video_name)
    
    return {"message": "Detección completada", "video_name": request.video_name, "output_folder": request.output_folder}
