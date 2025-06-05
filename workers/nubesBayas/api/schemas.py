from pydantic import BaseModel

class nubesRequest(BaseModel): 
    input_folder: str 
    output_folder: str 
    video_name: str
    baya_threshold: float
    qr_threshold: float
    cantidad_nubes: int
    calib_file: str 
    qr_dist: float 
    dists_list: list 
    num_points: int
    umbral_triangulacion: float
    max_workers_triangulacion: int
    
