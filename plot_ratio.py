import glob, json, os
import numpy as np
import pandas as pd
import pylab as plt
import seaborn as sns

F_JSON = glob.glob("data/summary/*.json")

df = pd.DataFrame([json.loads(open(f).read()) for f in F_JSON])
dfx = pd.read_csv("docs/source_movies.csv").set_index('source')

df['f_movie'] = df['f_movie'].apply(os.path.basename)
df = df.set_index('f_movie')
df['name'] = dfx['name']
#df = df.set_index('name')

def func(x):
    if len(x)>18: x=x[:15]+'...'
    return x

df['name'] = df['name'].apply(func)
df = df.set_index('name')


xkey = 'fraction_female_or_mixed_screentime'

df[xkey] = (
    df['fraction_female_face_screentime'] +
    df['fraction_mixed_face_screentime']
)
ykey = 'avg_frames_with_faces'


#sns.distplot(df.avg_frames_with_faces)
#plt.show()

#df[xkey] *= 2
#df[xkey] -= 1

fig, ax = plt.subplots(figsize=(9,8))
plt.scatter(df[xkey], df[ykey], s=10, alpha=0.85)

plt.xlabel(r"More males $\leftarrow$ Gender $\rightarrow$ More females")
plt.ylabel(r"Less faces $\leftarrow$ Scenery $\rightarrow$ More faces")

X = np.linspace(0,1,100)
Z = [.5,]*100
plt.plot(X,Z,'r--',alpha=0.25)
plt.plot(Z,X,'r--',alpha=0.25)

plt.ylim(0,1)
plt.xlim(0,1)


for x,y,text in zip(df[xkey], df[ykey],df.index):
    if len(text) > 15:
        text = text[:15] + '...'

    print x,y
    t = plt.text(x, y, text, zorder=-10)
    t.set_bbox(dict(facecolor='white', alpha=0.5, edgecolor='white'))

sns.despine()
plt.tight_layout()
plt.savefig("docs/ratio_plot.png")
plt.show()
