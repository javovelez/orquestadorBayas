from pydantic import BaseModel
from typing import Optional

class ProcesarVideoRequest(BaseModel):
    input_folder: str
    output_folder: str
    video_name: str
    num_processes: int = 4
    generar_video: bool = True
    factor_lentitud: float = 0.5
