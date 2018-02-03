import sys
import os
import glob
import joblib
import json
import numpy as np
import pandas as pd
from tqdm import tqdm

from imutils.face_utils import FaceAligner
import cv2
import dlib


args = {
    "--n_upsample":1,
    "--output_width":160,
    "--f_movie":sys.argv[1],
    "--extension":".jpg",
}

f_shape_predictor = "models/shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(f_shape_predictor)
face = FaceAligner(predictor,
                   desiredFaceWidth=args["--output_width"])


assert(os.path.exists(args["--f_movie"]))

name = os.path.basename(args["--f_movie"])
output_dir_faces = os.path.join('data',"faces/", name)
output_dir_json = os.path.join('data',"json/", name)
os.system('mkdir -p "{}"'.format(output_dir_json))
os.system('mkdir -p "{}"'.format(output_dir_faces))

image_dir = os.path.join('data',"frames/", name)
IMAGES = glob.glob(os.path.join(image_dir, "*"))
assert(IMAGES)


def process_image(f_img, skip_if_exists=True):
    '''
    Finds the largest face detected and saves it to disk.
    Writes an empty file if no face is found.
    '''

    f_json = os.path.join(
        output_dir_json,
        os.path.basename(f_img).replace(args["--extension"],'.json')
    )

    if skip_if_exists and os.path.exists(f_json):
        return False
    
    item = {
        "f_img_in":f_img,
        "frame_number":int(os.path.basename(f_img).split('.')[0]),
    }

    image = cv2.imread(f_img, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    rects, scores, robots = detector.run(
        gray,
        upsample_num_times=args["--n_upsample"],
    )
    
    item["faces_detected"] = len(rects)
    item["faces"] = []
    
    for k,(r,s) in enumerate(zip(rects, scores)):
        item_face = {
            "x0":r.right(),
            "x1":r.left(),
            "y0":r.top(),
            "y1":r.bottom(),           
            "score":s,
        }

        ext = args["--extension"]
        img_out = face.align(image, gray, r)
        item_face["f_img"] = os.path.join(
            output_dir_faces,
            
            os.path.basename(f_img).replace(ext,'_{:03d}.{}'.format(k,ext)),
        )

        cv2.imwrite(item_face["f_img"], img_out)
        item["faces"].append(item_face)
    
    with open(f_json,'w') as FOUT:
        FOUT.write(json.dumps(item, indent=2))

    return True

if __name__ == "__main__":

    with joblib.Parallel(-1) as MP:
        func = joblib.delayed(process_image)
        data = [x for x in MP(func(x) for x in tqdm(IMAGES))]
