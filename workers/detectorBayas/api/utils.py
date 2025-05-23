import json
import os
import cv2
import torch
import numpy as np


def get_directories(path):
    """
    Retorna una lista con los nombres de los directorios en la ruta especificada.
    """
    # Obtenemos una lista con todos los elementos en la ruta
    elementos = os.listdir(path)

    # Filtramos los elementos que sean directorios
    directorios = [elem for elem in elementos if os.path.isdir(os.path.join(path, elem))]

    return directorios

def create_output_directories(root, directories_list):
    path_of, of = os.path.split(root[:-1])
    path_to_look, _ = os.path.splitext(path_of)
    for directory in directories_list:
        if not os.path.isdir(root+directory) and os.path.exists(path_to_look+'/'+directory+'/input.txt'):
            os.mkdir(root+directory)


def process_videos(opt, video_name='video'):

    cam = cv2.VideoCapture(opt.demo)
    print('video:', opt.demo)
    opt.detector_for_track.pause = False
    frame_number=0
    flag = True
    dets = dict()
    while flag:
        # print('frame:', frame_number)
        flag, img = cam.read()
        if not flag :#or fr == 300
            break
        # cv2.imshow('input', img)
        ret = opt.detector_for_track.run_det_for_byte(img)[1]
        ret = ret.astype(np.float)
        ret = filter(lambda x: x[0]>0 and x[1]>0, ret)
        dets[frame_number] = { k:list(r[:3]) for k,r in enumerate(ret)}
        frame_number += 1
        print(f'video:{video_name}, frame number: {frame_number}')

    json.dump(dets, open(os.path.join(opt.output_folder_json, video_name + '.json'), 'w'))
