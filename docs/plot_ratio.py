import glob, json, os
import numpy as np
import pandas as pd
import pylab as plt
import seaborn as sns
#from matplotlib import rc
#rc('text', usetex=True)

cmap = sns.color_palette("RdBu_r", 8)
marker_size = 150
line_width = 1.0

F_JSON = glob.glob("../data/summary/*.json")[:]

df = pd.DataFrame([json.loads(open(f).read()) for f in F_JSON])
dfx = pd.read_csv("source_movies.csv").set_index('source')

df['f_movie'] = df['f_movie'].apply(os.path.basename)
df = df.set_index('f_movie')
df['name'] = dfx['name']
df['year'] = dfx['year']


# Clip years to be in scope
min_year = 1940
df["year"] = np.clip(df["year"], min_year, 2020)-min_year
df["color"] = (df.year/10.).astype(int)
colors = [cmap[x] for x in df["color"]]



def func(x):
    if type(x)==float: return x
    if len(x)>18: x=x[:15]+'...'
    return x

df['name'] = df['name'].apply(func)

idx = pd.isnull(df.name)
df.ix[idx, 'name'] = df.index[idx]

df = df.set_index('name')
xkey = 'fraction_female_or_mixed_screentime'

df[xkey] = (
    df['fraction_female_face_screentime'] +
    df['fraction_mixed_face_screentime']
)
ykey = 'avg_frames_with_faces'

###########################################################################

fig, ax = plt.subplots(figsize=(9,8))

plt.xlabel(r"More males $\leftarrow$ Gender $\rightarrow$ More females",
           fontsize=18)
plt.ylabel(r"Less faces $\leftarrow$ Scenery $\rightarrow$ More faces",
           fontsize=18)

X = np.linspace(0,1,100)
Z = [.5,]*100
plt.plot(X,Z,'k--',alpha=0.20,zorder=-3)
plt.plot(Z,X,'k--',alpha=0.20,zorder=-3)

plt.ylim(0,1)
plt.xlim(0,1)

sns.despine()
plt.tight_layout()

plt.savefig("figures/ratio_plot_empty.png")

S = plt.scatter(df[xkey], df[ykey],
                color=colors, lw=line_width, edgecolor='k',
                s=marker_size, alpha=0.65, zorder=-1,)

plt.savefig("figures/ratio_plot_years.png")

#S.set_sizes(marker_size/4)


T = []
for x,y,text in zip(df[xkey], df[ykey],df.index):

    # Clip long titles
    if len(text) > 15:
        text = text[:15] + '...'

    t = plt.text(x, y+0.015, text, zorder=-2)
    t.set_bbox(dict(facecolor='white', alpha=0.5, edgecolor='white'))
    T.append(t)



plt.savefig("figures/ratio_plot_titles.png")
plt.show()
