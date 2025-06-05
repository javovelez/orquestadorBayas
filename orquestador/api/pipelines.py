def pipeline_qr_detector(celery_app, video_folder, video_name, num_processes, generar_video, factor_lentitud):
    
    return celery_app.signature(
        'tasks.qr_detector_http_task',
        kwargs={
            'input_folder': video_folder,
            'output_folder': video_folder,
            'video_name': video_name,
            'num_processes': num_processes,
            'generar_video': generar_video,
            'factor_lentitud': factor_lentitud 
        }, 
        queue='peticiones_queue',
        task_id=f'{video_name}_qrdetector'
    )
    
def pipeline_detector_bayas(celery_app, video_folder, video_name):
        
    return celery_app.signature(
        'tasks.detector_http_task',
        kwargs = {
            'input_folder': video_folder,
            'output_folder': video_folder,
            'video_name': video_name
        },
        queue='peticiones_queue',
        task_id=f'{video_name}_detector'
    )

def pipeline_tracker(celery_app, video_folder, radius, video_name, draw_circles, draw_tracking):
    
    return celery_app.signature(
        'tasks.tracker_http_task',
        kwargs = {
            'input_folder': video_folder,
            'output_folder': video_folder,
            'video_name': video_name,
            'radius': radius,
            'draw_circles': draw_circles,
            'draw_tracking': draw_tracking
        },
        queue='peticiones_queue',
        task_id=f'{video_name}_tracker'
    )
    
def pipeline_nubes(celery_app, 
                   input_folder, 
                   output_folder, 
                   video_name, 
                   baya_thresh,
                   qr_thresh,
                   cant_nubes,
                   calib_file,
                   qr_dist,
                   dists_list,
                   reproy_csv_name, 
                   num_points): 
    
    return celery_app.signature(
        'tasks.nubes_http_task',
        kwargs = {
            'input_folder': input_folder,
            'output_folder': output_folder,
            'video_name': video_name,
            'baya_thresh': baya_thresh,
            'qr_thres': qr_thresh,
            'qr_dist': qr_dist,
            'cant_nubes': cant_nubes,
            'calib_file': calib_file,
            'dists_list': dists_list,
            'reproy_csv_name': reproy_csv_name,
            'num_points': num_points
        },
        queue='peticiones_queue',
        task_id=f'{video_name}_nubes'
    )
