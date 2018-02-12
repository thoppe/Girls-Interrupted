# https://github.com/davidsandberg/facenet/blob/master/src/compare.py

import glob
import os
import sys
import json

args = {
    "--batch_size":2**8,
    "--f_movie":sys.argv[1],
    "--f_model":"models/20170512-110547/20170512-110547.pb",
    "--save_dest":"data/embeddings",
}

name = os.path.basename(args["--f_movie"])
os.system('mkdir -p "{--save_dest}"'.format(**args))
f_save = os.path.join(args["--save_dest"], name+'.h5')

if os.path.exists(f_save):
    print "Already computed embedding for {}".format(name)
    exit()
#######################################################################

import h5py
from tqdm import tqdm   
import cv2
import numpy as np
import src.facenet.facenet as facenet
import tensorflow as tf

image_dir = os.path.join('data',"facenet_json/", name)
f_model_path = "./models"

JSON = sorted(glob.glob(os.path.join(image_dir, "*.json")))
assert(JSON)

def load_image(f_img):
    image = cv2.imread(f_img, cv2.IMREAD_COLOR)
    return image

def image_iterator():
    block = []

    for f in tqdm(JSON):
        with open(f) as FIN:
            js = json.loads(FIN.read())

        frame_idx = os.path.basename(f)
        frame_idx = int(frame_idx.split('.')[0])

        for k,face in enumerate(js['faces']):
            img = load_image(face['f_img'])
            block.append([frame_idx, k, img])

            if len(block) == args['--batch_size']:
                yield block
                block = []
    if block:
        yield block


config = tf.ConfigProto()
config.gpu_options.allow_growth = True

with tf.Graph().as_default(), h5py.File(f_save, 'w') as h5:
    print "Building the tensorflow model"
    sess = tf.Session(config=config)
    facenet.load_model(args["--f_model"])

    images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
    embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
    phase_train_placeholder = tf.get_default_graph().get_tensor_by_name(
        "phase_train:0")


    FRAME_IDX = []
    FACE_IDX = []
    EMBEDDING = []
    
    for block in image_iterator():
        frame_idx, face_idx, imgs = zip(*block)
        imgs = np.array(imgs)
        imgs = facenet.prewhiten(imgs)

        # Run forward pass to calculate embeddings
        feed_dict = { images_placeholder: imgs, phase_train_placeholder:False }
        emb = sess.run(embeddings, feed_dict=feed_dict)

        FRAME_IDX.extend(frame_idx)
        FACE_IDX.extend(face_idx)
        EMBEDDING.extend(emb.tolist())

    h5['frame_idx'] = FRAME_IDX
    h5['face_idx'] = FACE_IDX
    h5['embedding'] = EMBEDDING
    
