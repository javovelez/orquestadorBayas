from pydantic import BaseModel

class UserRequest(BaseModel): 
    num_processes = 4
    generar_video_qr = True
    factor_lentitud = 0.5
    baya_thresh = 0.7*150
    qr_thresh = 120
    cant_nubes = 1 
    calib_file = 'MotorolaG200_Javo_Vertical.yaml'
    qr_dist = 2.1
    dists_list = [10, 40, 5], 
    reproy_csv_name = 'reproyecciones.csv'
    num_points = 100