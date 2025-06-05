import pandas as pd
import copy
import cv2
import os
import random
class Tracker:
    def __init__(self, columns, video_name, args, frame = 0):
        df = pd.DataFrame(columns=columns)
        self.video_name = video_name
        self.df = df
        self.frame = frame
        self.previous_ids_dict = {}
        self.current_ids_dict = {}
        self.id_ctr = 0
        self.args = args
        if args.video_path is not None:
            self.vs = cv2.VideoCapture(args.video_path)

    def draw_circle(self, img, center, radius, color=(23, 220, 75), thickness=1):
        img = cv2.circle(img, center, radius, color, thickness)

    def draw_circles(self, img):
        
        # Creo la carpeta donde se guardan los frames
        tracker_frames_folder = os.path.join(self.args.output, 'tracker_frames')
        os.makedirs(tracker_frames_folder, exist_ok=True)
        
        data = self.df
        labels = data[data['image_name']==self.video_name+f'_{self.frame}.png']
        # ['image_name', 'x', 'y', 'r', 'detection', 'track_id', 'label']
    
        for _, label in labels.iterrows():
            image_name, x, y, r, _ , track_id, _ = list(label)
            center = (round(x), round(y),)
            radius = round(r)
            if self.args.draw_circles:
                self.draw_circle(img, center, radius)
            text = f"{track_id}"
            cv2.putText(img, text, (round(x)-5, round(y)+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 0, 200), 2 )
            # (random.randint(0,255), random.randint(0,255), random.randint(0,255))          
                  
        cv2.imwrite(f'{tracker_frames_folder}/{str(self.video_name)}_{self.frame}_track.png', img)
        print(f"Frame {self.frame} procesado y guardado como {self.video_name}_{self.frame}_track.png")
        

    def init_ids(self, vector):
        
        # rotation = get_video_rotation(self.args.video_path)
        print(f"Procesando video en tracker (init_ids): {self.args.video_path}")

        
        self.id_ctr = len(vector) - 1 #contador de id
        for i, v in enumerate(vector.values()):
            self.previous_ids_dict[i] = i     # diccionario clave: previus detection index; valor:id
                                             # todas las detecciones anteriores tienen id
            self._add_to_bundle(v[0], v[1], v[2], i)
        
        if self.args.draw_tracking:
            flag, img = self.vs.read()
            if not flag:
                raise FileNotFoundError(f"Error: No se pudo leer el video {self.args.video_path}")
            
            # if rotation != 0:
            #     img = rotate_frame(img, rotation)
            
            self.draw_circles(img)
            
            

    def update_ids(self, correspondence_set, current, previous):
        self.current_ids_dict.clear()
        match_dict = { cv[0]:cv[1] for cv in correspondence_set}
        previous_matched = correspondence_set[:,0]
        current_matched = correspondence_set[:,1]
        # rotation = get_video_rotation(self.args.video_path)
        
        for idx, _ in enumerate(previous):
            if idx in  previous_matched:
                self.current_ids_dict[match_dict[idx]] = self.previous_ids_dict[idx]

        for idx, cv in enumerate(current.values()):
            if idx not in current_matched:
                self.id_ctr +=1
                self.current_ids_dict[idx] = self.id_ctr
                self._add_to_bundle(cv[0], cv[1], cv[2], self.current_ids_dict[idx])
            else:
                self._add_to_bundle(cv[0], cv[1], cv[2], self.current_ids_dict[idx])
        
        if self.args.draw_tracking:
            frame = self.vs.read()
            flag, img = frame
            
            if not flag:
                raise Exception()
            
            # if rotation != 0:
            #     img = rotate_frame(img, rotation)
            
            self.draw_circles(img)
        self.previous_ids_dict = copy.deepcopy(self.current_ids_dict)



    def _add_to_bundle(self, x, y, radius, track_id):
        #['image_name', 'x', 'y', 'r', 'detection', 'track_id', 'label']
        det = [f'{str(self.video_name)}_{self.frame}.png', x, y, radius,'detecting', track_id, 'baya']
        self.df.loc[len(self.df)] = det

    def write_results(self, output_path, name='tracker_detections.csv'):
        
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        csv_path = os.path.join(output_path, name)
            
        print(csv_path)
        self.df.sort_values('track_id', inplace=True)
        self.df.to_csv(csv_path)
        
def get_video_rotation(video_path):
    """Obtiene la rotación del video usando metadatos (FFmpeg/OpenCV no lo hace automáticamente)."""
    cap = cv2.VideoCapture(video_path)
    rotation = 0
    try:
        # Para videos MP4/MOV, la rotación puede estar en la metadata
        if cap.isOpened():
            # OpenCV no expone directamente la rotación, pero puedes usar FFmpeg o exiftool
            # Alternativa: Usar CAP_PROP_ORIENTATION (depende de la versión de OpenCV)
            rotation_code = int(cap.get(cv2.CAP_PROP_ORIENTATION_META))
            if rotation_code == 90:
                rotation = 90
            elif rotation_code == 180:
                rotation = 180
            elif rotation_code == 270:
                rotation = 270
    except:
        pass
    cap.release()
    return rotation

def rotate_frame(frame, rotation):
    """Rota el frame según el ángulo especificado."""
    if rotation == 90:
        return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    elif rotation == 180:
        return cv2.rotate(frame, cv2.ROTATE_180)
    elif rotation == 270:
        return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return frame

