# Clone the repo https://github.com/davidsandberg/facenet
# Set the path: export PYTHONPATH=~/src/facenet/src/

# https://github.com/davidsandberg/facenet
# Download the model 20170512-110547.zip
# Extract the model to ~/src/facenet/models/

import sys
import os
import glob
import joblib
import json
import numpy as np
import pandas as pd
from tqdm import tqdm

minsize = 50  # minimum size of face
threshold = [0.6, 0.7, 0.7]  # three steps's threshold
factor = 0.709  # scale factor

skip_if_exists = True

args = {
    "--n_upsample": 1,
    "--output_width": 160,
    "--f_movie": sys.argv[1],
    "--extension": ".jpg",
}

assert(os.path.exists(args["--f_movie"]))

name = os.path.basename(args["--f_movie"])
output_dir_faces = os.path.join('data', "facenet_faces/", name)
output_dir_json = os.path.join('data', "facenet_json/", name)
os.system('mkdir -p "{}"'.format(output_dir_json))
os.system('mkdir -p "{}"'.format(output_dir_faces))

image_dir = os.path.join('data', "frames/", name)


def get_f_json(f_img):
    f_json = os.path.join(
        output_dir_json,
        os.path.basename(f_img).replace(args["--extension"], '.json')
    )
    return f_json


def filter_image(f_img):
    return not os.path.exists(get_f_json(f_img))


def process_image(f_img, skip_if_exists=True):

    f_json = get_f_json(f_img)

    if skip_if_exists and os.path.exists(f_json):
        return False

    item = {
        "f_img_in": f_img,
        "frame_number": int(os.path.basename(f_img).split('.')[0]),
    }

    img = cv2.imread(f_img, cv2.IMREAD_COLOR)
    img_area = img.shape[0] * img.shape[1]

    #   run detect_face from the facenet library
    bounding_boxes, _ = align.detect_face(
        img, minsize, pnet,
            rnet, onet, threshold, factor)

    item["faces_detected"] = len(bounding_boxes)
    item["faces"] = []

    for k, (x0, y0, x1, y1, acc) in enumerate(bounding_boxes):

        item_face = {
            "x0": x0,
            "x1": x1,
            "y0": y0,
            "y1": y1,
            "score": acc,
        }

        area = abs(x0 - x1) * abs(y0 - y1)
        item_face["screen_fraction"] = area / img_area

        ext = args["--extension"]

        r = dlib.dlib.rectangle(int(x0), int(y0), int(x1), int(y1))

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_out = face.align(img, gray, r)

        item_face["f_img"] = os.path.join(
            output_dir_faces,
            os.path.basename(f_img).
            replace(ext, '_{:03d}{}'.format(k, ext)),
        )

        cv2.imwrite(item_face["f_img"], img_out)
        item["faces"].append(item_face)

    with open(f_json, 'w') as FOUT:
        FOUT.write(json.dumps(item, indent=2))

#

IMAGES = sorted(glob.glob(os.path.join(image_dir, "*")))
assert(IMAGES)

IMAGES = [x for x in IMAGES if filter_image(x)]
if not IMAGES:
    exit()

print "Starting", image_dir, len(IMAGES)



# Facenet import
import src.facenet.align.detect_face as align

from imutils.face_utils import FaceAligner
import cv2
import dlib
import tensorflow as tf


f_shape_predictor = "models/shape_predictor_68_face_landmarks.dat"
predictor = dlib.shape_predictor(f_shape_predictor)
face = FaceAligner(predictor,
                   desiredFaceWidth=args["--output_width"])

config = tf.ConfigProto()
config.gpu_options.allow_growth = True

#   Start code from facenet/src/compare.py
print('Creating networks and loading parameters')
with tf.Graph().as_default():
    print "Building the tensorflow model"
    sess = tf.Session(config=config)

    with sess.as_default():
        pnet, rnet, onet = align.create_mtcnn(sess, None)

    for f_img in tqdm(IMAGES):
        process_image(f_img)
