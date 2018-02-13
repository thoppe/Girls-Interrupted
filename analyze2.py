# -*- coding: utf-8 -*-
import json
import tqdm
import sys
import os
import glob
import numpy as np
import pandas as pd
import seaborn as sns
import pylab as plt

min_screen_fraction = 0.0015
min_score = 0.90

cmap = [
    #np.array([1, ] * 4) * 0.98,
    np.array( [.195, ] * 4) * 0.98,
    
    np.array([255, 44, 77, 255]) / 255.,
    np.array([0, 191, 187, 255]) / 255.,
    # np.array([0.5,]*4)*0.98,
]

args = {
    "--f_movie": sys.argv[1],
    "--max_frames": None,
    "--debug": False,
}

name = os.path.basename(args["--f_movie"])

os.system('mkdir -p figures/lineplots')
f_png = os.path.join('figures/lineplots', name + '.png')

os.system('mkdir -p data/summary')
f_summary = os.path.join('data/summary', name + '.json')
sdata = {}

if args["--debug"]:
    args["--max_frames"] = 500

F_JSON = sorted(glob.glob(os.path.join(
    "data", "facenet_json", name, "*.json")))


data = []
for f in tqdm.tqdm(F_JSON):
    with open(f) as FIN:
        js = json.loads(FIN.read())

    item = {
        "frame_number": js["frame_number"],
        "faces_detected": js["faces_detected"],
        "male": 0.0,
        "female": 0.0,
        "screen_fraction": 0.0,
    }

    for face in js['faces']:

        # If the face is too small, reject it completely
        if face['screen_fraction'] < min_screen_fraction:
            item['faces_detected'] -= 1
            continue

        # We the detector isn't sure of the face, reject it completely
        if face['score'] < min_score:
            item['faces_detected'] -= 1
            continue

        item['screen_fraction'] += face['screen_fraction']

        # Don't count gender if ambigous
        if face['gender'] > 0.35 and face['gender'] < 0.65:
            continue

        g = face["gender"]
        if g >= 0.5:
            item['male'] += g - 0.5
        elif g < 0.5:
            item['female'] += 0.5 - g

    data.append(item)

    mf = args["--max_frames"]
    if mf and len(data) >= mf:
        break


df = pd.DataFrame(data).sort_values('frame_number').set_index('frame_number')

sdata["f_movie"] = args["--f_movie"]
sdata["total_frames"] = len(df)
sdata["total_frames_with_faces"] = (df.faces_detected > 0).sum()

sdata["total_frames_with_male_faces"] = (df.male > 0).sum()
sdata["total_frames_with_female_faces"] = (df.female > 0).sum()
sdata["avg_face_screen_fraction"] = df['screen_fraction'].sum() / len(df)


item['screen_fraction'] = face['screen_fraction']

sdata["avg_frames_with_faces"] = (df.faces_detected > 0).mean()
sdata["avg_frames_with_male_faces"] = (df.male > 0).mean()
sdata["avg_frames_with_female_faces"] = (df.female > 0).mean()

dfx = df[df.faces_detected > 0]
sdata["fraction_female_face_screentime"] = ((dfx.female > 0) &
                                            (dfx.male == 0)).mean()
sdata["fraction_male_face_screentime"] = ((dfx.female == 0) &
                                          (dfx.male > 0)).mean()
sdata["fraction_mixed_face_screentime"] = ((dfx.female > 0) &
                                           (dfx.male > 0)).mean()

with open(f_summary, 'w') as FOUT:
    js = json.dumps(sdata, indent=2)
    FOUT.write(js)
    print(js)

X = np.zeros(shape=(2, len(df)), dtype=int)
X[0, :] = (df.female > 0)
X[1, :] = (df.male > 0) * 2
# X[1,:] = ((df.male>0) & (df.female>0))*3

# idx = X.sum(axis=0)==0
# X = X[:,~idx]

# fig, ax = plt.subplots(figsize=(10,2))
fig, ax = plt.subplots(figsize=(8, 1.0))

sns.heatmap(X, cmap=cmap, cbar=False, alpha=0.5,
            linecolor=None,
            linewidths=0,)

plt.axis('off')
ax.xaxis.set_ticks_position('none')
ax.yaxis.set_ticks_position('none')
#plt.yticks([.5, 1.5], [u'♀', u'♂'],
#           fontsize=20,
#           rotation='horizontal')
plt.xticks([], [])
plt.tight_layout(w_pad=-2.0, h_pad=-2.5)
plt.savefig(f_png, pad_inches=0,
            bbox_inches=0,
            #bbox_inches='tight',
            dpi=100)
print f_png

os.system('mogrify -trim "{}"'.format(f_png))

#if not args["--debug"]:
#    print("Completed", f_png)
# else:
#plt.show()
