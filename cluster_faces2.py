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

from sklearn.manifold import TSNE

args = {
    "--f_movie": sys.argv[1],
    "--load_dest": "data/embeddings",
    "--learning_rate": 300.0,
    "--min_samples": 20,
    "--save_dest": "figures/tSNE",
    "--n_jobs": 1,
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
    print("Already computed, skipping" + f_png2)
    exit()


def calculate_tSNE(f_h5):
    with h5py.File(f_h5, 'r+') as h5:

        if "tSNE" not in h5:
            print("Calculating tSNE embedding")

            print("Actually, skipping")
            exit()

            X = h5["embedding"][:]
            lr = args["--learning_rate"]
            h5["tSNE"] = TSNE(n_components=2,
                              learning_rate=lr).fit_transform(X)
            h5["tSNE"].attrs["learning_rate"] = lr


def apply_gender_calc(f_h5):

    with h5py.File(f_h5, 'r+') as h5:
        if "gender" not in h5:
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
            h5["gender"] = gender
            h5["screen_fraction"] = fraction


calculate_tSNE(f_h5)
apply_gender_calc(f_h5)

fig, ax = plt.subplots(1, 1, figsize=(8, 8))

with h5py.File(f_h5, 'r+') as h5:
    X = h5["embedding"][:]
    pts = h5["tSNE"][:]
    face_idx = h5["face_idx"][:]
    frame_idx = h5["frame_idx"][:]
    screen_fraction = h5["screen_fraction"][:]
    gender_exp = h5["gender"][:]

from sklearn.preprocessing import StandardScaler
pts = StandardScaler().fit_transform(pts)

cmap = sns.diverging_palette(240, 10, n=100)
gender_exp = np.clip(gender_exp * 100, 0, 100).astype(int)
colors = [cmap[n] for n in gender_exp]

plt.scatter(pts[:, 0], pts[:, 1], color=colors, lw=.1, edgecolor='k',
            alpha=0.90)
sns.despine(left=True, bottom=True)
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)
plt.tight_layout()
plt.savefig(f_png1)


#

clf = sklearn.cluster.MeanShift(bandwidth=.45, n_jobs=args["--n_jobs"])
labels = clf.fit_predict(pts)
label_counts = collections.Counter(labels)
print(label_counts)

CENTERS = []
for n in range(0, labels.max() + 1):
    idx = labels == n
    centroid_pts = pts[idx].mean(axis=0)

    # Removed old double index
    # idx2 = np.ones(idx.shape, dtype=True)
    idx3 = X[idx].dot(X[idx].mean(axis=0)).argmax()

    # clf = PCA(n_components=3)
    # clf.fit(X[idx])
    # x2 = clf.inverse_transform(clf.transform(X[idx]))
    # idx3 = ((X[idx]-x2)**2).sum(axis=1).argmin()

    i = frame_idx[idx][idx3]
    j = face_idx[idx][idx3]

    f_face = os.path.join("data/facenet_faces/", name,
                          "{:06d}_{:03d}.jpg".format(i, j))
    img = plt.imread(f_face)

    arr = OffsetImage(img, zoom=0.30)
    ab = AnnotationBbox(arr, centroid_pts,
                        xybox=(-40., 40.),
                        xycoords='data',
                        boxcoords="offset points",
                        pad=0,
                        # arrowprops=dict(arrowstyle="->",alpha=0.5),
                        )
    ax.add_artist(ab)

    CENTERS.append(centroid_pts)

print "Completed", f_png2
plt.savefig(f_png2)
