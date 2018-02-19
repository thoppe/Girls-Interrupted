import h5py
from tqdm import tqdm
import sys
import os
import collections
import json
import numpy as np
import pylab as plt
import seaborn as sns
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

import sklearn
import sklearn.cluster

args = {
    "--f_movie": sys.argv[1],
    "--load_dest": "data/embeddings",
    "--learning_rate": 300.0,
    "--min_samples": 15,
    "--save_dest": "figures/tSNE",
    "--n_jobs": 1,
    "--min_screen_fraction":0.0015,
    "--min_face_score":0.90,
    "--meanshift_bandwidth":0.425,
}

name = os.path.basename(args["--f_movie"])
f_h5 = os.path.join(args["--load_dest"], name + '.h5')

if not os.path.exists(f_h5):
    print("Need to compute embedding first")
    exit()

f_png1 = os.path.join(args["--save_dest"], "points", name + '.png')
f_png2 = os.path.join(args["--save_dest"], "images", name + '.png')
os.system('mkdir -p {}'.format(os.path.join(args["--save_dest"], "points")))
os.system('mkdir -p {}'.format(os.path.join(args["--save_dest"], "images")))

if os.path.exists(f_png2):
    print("Already computed, skipping " + f_png2)
    exit()


def calculate_tSNE(f_h5):
    
    from sklearn.manifold import TSNE

    with h5py.File(f_h5, 'r+') as h5:

        if "tSNE" not in h5:
            print("Calculating tSNE embedding")

            #print("Actually, skipping")
            #exit()

            X = h5["embedding"][:]
            lr = args["--learning_rate"]
            h5["tSNE"] = TSNE(n_components=2,
                              learning_rate=lr).fit_transform(X)
            h5["tSNE"].attrs["learning_rate"] = lr


def apply_gender_calc(f_h5):

    with h5py.File(f_h5, 'r+') as h5:
        if "face_detection_score" not in h5:

            for key in "gender","screen_fraction","face_detection_score":
                if key in h5: del h5[key]

            score = []
            gender = []
            fraction = []

            face_idx = h5["face_idx"][:]
            frame_idx = h5["frame_idx"][:]

            for i, j in tqdm(zip(frame_idx, face_idx)):
                f_face = os.path.join("data/facenet_json/", name,
                                      "{:06d}.json".format(i,))
                with open(f_face) as FIN:
                    js = json.loads(FIN.read())["faces"][j]
                    gender.append(js["gender"])
                    fraction.append(js["screen_fraction"])
                    score.append(js["score"])
            h5["gender"] = gender
            h5["screen_fraction"] = fraction
            h5["face_detection_score"] = score


calculate_tSNE(f_h5)
apply_gender_calc(f_h5)

fig, ax = plt.subplots(1, 1, figsize=(8, 8))

with h5py.File(f_h5, 'r+') as h5:
    screen_fraction = h5["screen_fraction"][...]
    face_score = h5["face_detection_score"][...]

    # Drop the low screen fraction points or score
    idx0 = screen_fraction>args["--min_screen_fraction"]
    idx1 = face_score>args["--min_face_score"]
    idx = idx0&idx1
    
    screen_fraction = screen_fraction[idx]
    face_score = face_score[idx]
    
    X = h5["embedding"][...][idx]
    pts = h5["tSNE"][...][idx]
    face_idx = h5["face_idx"][...][idx]
    frame_idx = h5["frame_idx"][...][idx]
    gender_exp = h5["gender"][...][idx]

    

from sklearn.preprocessing import StandardScaler
pts = StandardScaler().fit_transform(pts)

cmap = np.array(sns.diverging_palette(240, 10, n=100))[::-1]

gender_exp = np.clip(gender_exp * 100, 0, 100).astype(int)
colors = [cmap[n] for n in gender_exp]

lw = np.ones(pts.shape[0],dtype=float)*0.1
idx = (gender_exp>65) | (gender_exp<35)
lw[idx] *= 5

plt.scatter(pts[:, 0], pts[:, 1], color=colors,
            lw=lw, edgecolor='k',
            alpha=0.90)
sns.despine(left=True, bottom=True)
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)
plt.tight_layout()
plt.savefig(f_png1)


#

clf = sklearn.cluster.MeanShift(
    bandwidth=args["--meanshift_bandwidth"], n_jobs=args["--n_jobs"])
labels = clf.fit_predict(pts)
label_counts = collections.Counter(labels)
print(label_counts)

CENTERS = []
for n in range(0, labels.max() + 1):
    idx = labels == n
    centroid_pts = pts[idx].mean(axis=0)

    # Take the center face
    idx3 = X[idx].dot(X[idx].mean(axis=0)).argmax()

    i = frame_idx[idx][idx3]
    j = face_idx[idx][idx3]

    f_face = os.path.join("data/facenet_faces/", name,
                          "{:06d}_{:03d}.jpg".format(i, j))
    img = plt.imread(f_face)
    #print screen_fraction[idx][idx3], f_face

    # Adjust pics on left side
    dx = -40
    if centroid_pts[0] < 0:
        dx += 20

    arr = OffsetImage(img, zoom=0.30)
    ab = AnnotationBbox(arr, centroid_pts,
                        xybox=(dx, 40.),
                        xycoords='data',
                        boxcoords="offset points",
                        pad=0,
                        # arrowprops=dict(arrowstyle="->",alpha=0.5),
                        )
    ax.add_artist(ab)

    CENTERS.append(centroid_pts)

print "Completed", f_png2
plt.savefig(f_png2)
#plt.show()
