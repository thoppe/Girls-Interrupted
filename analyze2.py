# -*- coding: utf-8 -*-
import glob, json, tqdm, sys, os
import numpy as np
import pandas as pd
import seaborn as sns
import pylab as plt

cmap = [
    np.array([1,]*4)*0.98,
    np.array([255,44,77,255])/255.,
    np.array([0,191,187,255])/255.,
    #np.array([0.5,]*4)*0.98,
]

args = {
    "--f_movie":sys.argv[1],
    "--max_frames":None,
    "--debug":False,
}

os.system('mkdir -p figures')
name = os.path.basename(args["--f_movie"])

if args["--debug"]:
    args["--max_frames"]=500

F_JSON = sorted(glob.glob(os.path.join(
    "data","facenet_json",name,"*.json")))


data = []
for f in tqdm.tqdm(F_JSON):
    with open(f) as FIN:
        js = json.loads(FIN.read())
    
    item = {
        "frame_number":js["frame_number"],
        "faces_detected":js["faces_detected"],
        "male":0.0,
        "female":0.0,
    }

    for face in js['faces']:
        g = face["gender"]
        if g>=0.5:
            item['male'] += g - 0.5
        elif g<0.5:
            item['female'] += 0.5 - g

        dx = abs(face['x0']-face['x1'])
        dy = abs(face['y0']-face['y1'])

        
        item['area'] = float(dx*dy)
            
    data.append(item)

    mf = args["--max_frames"] 
    if mf and len(data)>= mf:
        break

    
df = pd.DataFrame(data).sort_values('frame_number').set_index('frame_number')
print df[df.female>0]
#print df.male.mean()
#print df.female.mean()
#exit()

X = np.zeros(shape=(2,len(df)),dtype=int)
X[0,:] = (df.female>0)
X[1,:] = (df.male>0)*2
#X[1,:] = ((df.male>0) & (df.female>0))*3

#idx = X.sum(axis=0)==0
#X = X[:,~idx]

#fig, ax = plt.subplots(figsize=(10,2))
fig, ax = plt.subplots(figsize=(10,1.5))

sns.heatmap(X, cmap=cmap, cbar=False, alpha=0.5,
            linecolor=None,
            linewidths=0,)
#plt.axis('off')
ax.xaxis.set_ticks_position('none')
ax.yaxis.set_ticks_position('none') 
plt.tight_layout()
plt.yticks([.5,1.5], [u'♀',u'♂'],
           fontsize=20,
           rotation='horizontal')
plt.xticks([],[])

if not args["--debug"]:
    f_png = os.path.join('figures', name + '.png')
    plt.savefig(f_png,bbox_inches='tight', dpi=100)
    print "Completed", f_png
#else:
#plt.show()


