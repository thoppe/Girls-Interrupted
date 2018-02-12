import cv2
import glob
import os
import sys
import json
from tqdm import tqdm
import tensorflow as tf
import src.inception_resnet_v1

args = {
    "--batch_size": 256,
    "--f_movie": sys.argv[1],
}

assert(os.path.exists(args["--f_movie"]))

name = os.path.basename(args["--f_movie"])
image_dir = os.path.join('data', "facenet_json/", name)
f_model_path = "./models"
gkey = "gender_expression"

JSON = glob.glob(os.path.join(image_dir, "*.json"))
assert(JSON)


def load_image(f_img):
    image = cv2.imread(f_img, cv2.IMREAD_COLOR)
    return image


def image_iterator():
    block = []

    for f in tqdm(JSON):
        with open(f) as FIN:
            try:
                js = json.loads(FIN.read())
            except ValueError as Ex:
                print Ex
                print f
                raise(Ex)

        for k, face in enumerate(js['faces']):
            if gkey not in face:
                img = load_image(face['f_img'])
                block.append([f, k, img])

                if len(block) == args['--batch_size']:
                    yield block
                    block = []
    if block:
        yield block

data = []

config = tf.ConfigProto()
config.gpu_options.allow_growth = True

with tf.Graph().as_default():
    print("Building the tensorflow model")
    sess = tf.Session(config=config)

    images_in = tf.placeholder(
        tf.float32,
        shape=[None, 160, 160, 3],
        name='input_image')
    images = tf.map_fn(
        lambda frame: tf.reverse_v2(frame,
                                    [-1]),
        images_in)  # BGR TO RGB
    images_norm = tf.map_fn(
        lambda frame: tf.image.per_image_standardization(frame),
        images)
    train_mode = tf.placeholder(tf.bool)
    age_logits, gender_logits, _ = src.inception_resnet_v1.inference(
        images_norm,
        keep_probability=0.8,
        phase_train=train_mode,
        weight_decay=1e-5)

    gender = tf.nn.softmax(gender_logits)
    age_ = tf.cast(tf.constant([i for i in range(0, 101)]), tf.float32)
    age = tf.reduce_sum(tf.multiply(tf.nn.softmax(age_logits), age_), axis=1)

    init_op = tf.group(
        tf.global_variables_initializer(),
        tf.local_variables_initializer()
    )
    sess.run(init_op)

    print("Restoring the saved model")
    saver = tf.train.Saver()
    ckpt = tf.train.get_checkpoint_state(f_model_path)
    saver.restore(sess, ckpt.model_checkpoint_path)

    for block in image_iterator():
        f_jsons, ks, imgs = zip(*block)

        feed_args = {images_in: imgs, train_mode: False}
        age_res, gender_res = sess.run([age, gender], feed_dict=feed_args)

        for f, ax, gx, k in zip(f_jsons, age_res, gender_res, ks):
            data.append({
                "age": float(ax),
                "gender": float(gx[1]),
                "f_json": f, "k": k
            })


# Save the data to disk
for row in data:
    with open(row["f_json"], 'r') as FIN:
        js = json.loads(FIN.read())
        js['faces'][row['k']]['age'] = row['age']
        js['faces'][row['k']]['gender'] = row['gender']

    with open(row["f_json"], 'w') as FOUT:
        FOUT.write(json.dumps(js, indent=2))
