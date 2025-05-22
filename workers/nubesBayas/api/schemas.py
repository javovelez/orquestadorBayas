from pydantic import BaseModel

class nubesRequest(BaseModel): 
    input_folder: str 
    output_folder: str 
    video_name: str
    baya_threshold: float = 0.7*150
    qr_threshold: float = 120
    cantidad_nubes: int = 1
    calib_file: str = 'MotorolaG200_Javo_Vertical.yaml'
    qr_dist: float = 2.1
    init_distance: int = 15
    dists_list: list = [10, 40, 5]
    min_mer: float = 10
    min_dist: int = 0
    min_path: str = ''
    reproy_csv_name: str = 'Reproyecciones.csv'
    num_points: int = 100
    
