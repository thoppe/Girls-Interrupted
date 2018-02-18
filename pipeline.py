'''
Looks for any file in raw_videos/* and runs it through
the standard pipeline:

[create_frames]-[segment_faces]-[predict_images]-[analyze]

# Set the path: export PYTHONPATH=~/src/facenet/src/
'''
import glob
import os
import joblib
import random

args = {
    "--force": False,
}

def f_movie_queue():

    F_MOVIE = glob.glob("raw_videos/*")[::-1]
    random.shuffle(F_MOVIE)

    for f in F_MOVIE:
        name = os.path.basename(f)
        f_png = os.path.join("figures/tSNE/images/", name + '.png')

        if os.path.exists(f_png):
            continue
        
        yield f

def f_queue():

    F_MOVIE = glob.glob("raw_videos/*")[::-1]
    random.shuffle(F_MOVIE)

    for f in F_MOVIE:
        name = os.path.basename(f)
        f_png = os.path.join("figures", "lineplots", name + '.png')

        if os.path.exists(f_png) and not args['--force']:
            continue

        yield f


def func_frames(f):
    print("Starting", f)
    os.system("python create_frames.py '{}'".format(f))

def func_segment(f):
    os.system("python facenet_segment.py '{}'".format(f))

def func_predict(f):
    os.system("python predict_images2.py '{}'".format(f))

def func_analyze(f):
    os.system("python analyze2.py '{}'".format(f))

def func_embed(f):
    os.system("python calculate_embeddings.py '{}'".format(f))

def func_cluster(f):
    os.system("python cluster_faces2.py '{}'".format(f))

    
if __name__ == "__main__":

    
    func = joblib.delayed(func_frames)
    with joblib.Parallel(4, batch_size=1) as MP:
        MP(func(x) for x in f_queue())

    func = joblib.delayed(func_segment)
    with joblib.Parallel(4, batch_size=1) as MP:
        MP(func(x) for x in f_queue())

    map(func_predict, f_queue())
    
    func = joblib.delayed(func_analyze)
    with joblib.Parallel(-1) as MP:
        MP(func(x) for x in f_queue())
    
    func = joblib.delayed(func_embed)
    with joblib.Parallel(1) as MP:
        MP(func(x) for x in f_movie_queue())
    
    func = joblib.delayed(func_cluster)
    with joblib.Parallel(-1) as MP:
        MP(func(x) for x in f_movie_queue())
    
