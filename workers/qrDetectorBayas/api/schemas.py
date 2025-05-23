from pydantic import BaseModel
from typing import Optional

class ProcesarVideoRequest(BaseModel):
    video_name: str
    input_folder: str
    output_folder: str
    log_path: str
    num_processes: int = 4
    generar_video: bool = True
    factor_lentitud: float = 0.5
