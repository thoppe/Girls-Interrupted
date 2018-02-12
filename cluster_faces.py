import h5py
import sys, os, collections
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.manifold import TSNE
import pylab as plt
import seaborn as sns
from matplotlib.offsetbox import  OffsetImage, AnnotationBbox

args = {
    "--f_movie":sys.argv[1],
    "--load_dest":"data/embeddings",
    "--learning_rate": 300.0,
    "--min_samples":30,
    "--force":False,
}

name = os.path.basename(args["--f_movie"])
f_h5 = os.path.join(args["--load_dest"], name+'.h5')

if not os.path.exists(f_h5):
    print "Need to compute embedding first"
    exit()

f_png = os.path.join("tSNE", name + '.png')
if os.path.exists(f_png):
    print "Already computed, skipping", f_png
    exit()

clf = DBSCAN(
    #eps=.8,
    eps=0.27,
    metric='cosine',
    min_samples=args["--min_samples"],
    metric_params=None, algorithm='auto',
    leaf_size=30, n_jobs=1)


def calculate_tSNE(f_h5):
    with h5py.File(f_h5,'r+') as h5:

        if "tSNE" not in h5 or args["--force"]:
            if "tSNE" in h5:
                del h5["tSNE"]
            
            print "Calculating tSNE embedding"
            X = h5["embedding"][:]
            lr = args["--learning_rate"]
            h5["tSNE"] = TSNE(n_components=2,
                              learning_rate=lr).fit_transform(X)
            h5["tSNE"].attrs["learning_rate"] = lr

calculate_tSNE(f_h5)

fig, ax = plt.subplots(1, 1, figsize=(8, 8))
            
with h5py.File(f_h5,'r+') as h5:
    X = h5["embedding"][:]
    pts = h5["tSNE"][:]
    face_idx = h5["face_idx"][:]
    frame_idx = h5["frame_idx"][:]

from sklearn.preprocessing import StandardScaler
pts = StandardScaler().fit_transform(pts)


labels = clf.fit_predict(X)
label_counts = collections.Counter(labels)
print label_counts

CENTERS = []
for n in range(0, labels.max()+1):
    idx = labels==n
    centroid_pts = pts[idx].mean(axis=0)

    idx2 = X[idx].dot(X[idx].mean(axis=0)).argmax()
    i = frame_idx[idx][idx2]
    j = face_idx[idx][idx2]

    f_face = os.path.join("data/facenet_faces/", name,
                          "{:06d}_{:03d}.jpg".format(i,j))
    img = plt.imread(f_face)

    x,y = centroid_pts
    #x += 160/2
    #y += 160/2
    #print x,y

    arr = OffsetImage(img, zoom=0.30)

    ab = AnnotationBbox(arr, [x,y],
                        xybox=(-40., 40.),
                        xycoords='data',
                        boxcoords="offset points",
                        pad=0,
                        arrowprops=dict(arrowstyle="->"),
    )
    ax.add_artist(ab)   
    
    CENTERS.append(centroid_pts)

    
CENTERS = np.array(CENTERS)
plt.scatter(CENTERS[:,0], CENTERS[:,1], s=50,
            color='k',zorder=-1,
            alpha=0.25)

n_colors = labels.max()
cmap = sns.color_palette('hls', n_colors+1)
colors = [cmap[n] if n>-1 else [1,1,1,0.25] for n in labels]


plt.scatter(pts[:,0], pts[:,1], color=colors, lw=.1,edgecolor='k')
sns.despine(left=True, bottom=True)
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)
plt.xlim(-20.5,2.5)
plt.ylim(-20.5,2.5)
plt.axis('square')
plt.tight_layout()


plt.savefig(f_png)
#plt.show()

