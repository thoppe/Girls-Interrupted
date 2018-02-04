'''
Looks for any file in raw_videos/* and runs it through 
the standard pipeline:

[create_frames]-[segment_faces]-[predict_images]-[analyze]
'''
import glob, os, joblib

def f_queue():

    F_MOVIE = glob.glob("raw_videos/*")

    for f in F_MOVIE:
        name = os.path.basename(f)
        f_png = os.path.join("figures", name+'.png')

        if os.path.exists(f_png):
            continue

        yield f

def process(f):
    print "Starting", f
    os.system("python create_frames.py '{}'".format(f))
    #os.system("python segment_faces.py '{}'".format(f))
    #os.system("python predict_images.py '{}'".format(f))
    #os.system("python analyze.py '{}'".format(f))

if __name__ == "__main__":
    func = joblib.delayed(process)
    with joblib.Parallel(1) as MP:
        MP(func(x) for x in f_queue())

