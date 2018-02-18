import glob, json, os
import numpy as np
import pandas as pd
import pylab as plt
import seaborn as sns


marker_size = 150
line_width = 1.0
df = pd.read_csv("source_movies.csv")

# Clip years to be in scope
min_year = 1940
df["clip_year"] = np.clip(df["year"], min_year, 2020)-min_year
df["color"] = (df.clip_year/10.).astype(int)

def clip_text(x):
    if type(x)==float: return x
    if len(x)>18: x=x[:15]+'...'
    return x

df['name'] = df['name'].apply(clip_text)

idx = pd.isnull(df.name)
df.ix[idx, 'name'] = df.index[idx]

df = df.set_index('name')
xkey = 'fraction_female_or_mixed_screentime'

df[xkey] = (
    df['fraction_female_face_screentime'] +
    df['fraction_mixed_face_screentime']
)
ykey = 'avg_frames_with_faces'
zkey = 'year'

###########################################################################

f, axes = plt.subplots(2, 1, figsize=(9, 6))#, sharex=True)

df["Year"] = map(lambda x:round(x,-1), df.year)
df["Year"] = np.clip(df["Year"], 1940, 2010).astype(int)

cmap = sns.color_palette("PRGn", 8)

sns.barplot(data=df,x='Year',y=ykey,ax=axes[0],color=cmap[1])
axes[0].set_ylabel("Facetime")
sns.barplot(data=df,x='Year',y=xkey,ax=axes[1],color=cmap[-2])
axes[1].set_ylabel("Relative female\nscreentime")
sns.despine()
plt.tight_layout()
plt.savefig("figures/barplot_yearsVsFaceAndFemales.png")

###########################################################################


fig, ax = plt.subplots(figsize=(9,8))

plt.xlabel(r"More males $\leftarrow$ Gender $\rightarrow$ More females",
           fontsize=18)
plt.ylabel(r"Less faces $\leftarrow$ Scenery $\rightarrow$ More faces",
           fontsize=18)

plt.setp(ax.get_xticklabels(), fontsize=16)
plt.setp(ax.get_yticklabels(), fontsize=16)

X = np.linspace(0,1,100)
Z = [.5,]*100
plt.plot(X,Z,'k--',alpha=0.20,zorder=-3)
plt.plot(Z,X,'k--',alpha=0.20,zorder=-3)

plt.ylim(0,1)
plt.xlim(0,1)

sns.despine()
plt.tight_layout()

plt.savefig("figures/ratio_plot_empty.png")

scatter_kwargs = {
    "lw":line_width,
    "zorder":-1,
    "edgecolor":'k',
    "s":marker_size,
    "alpha":0.65,
}


dfx = df.dropna(subset=["BECHDEL_rating"])
BTcmap = sns.diverging_palette(145, 280, s=85, l=25, n=4)
SP = []
for k, color in enumerate(BTcmap):
    idx = dfx["BECHDEL_rating"]==k
    SP.append(plt.scatter(dfx[idx][xkey], dfx[idx][ykey],
                          color=color, 
                          label="Bechdel score: {}".format(k),
                          **scatter_kwargs))
    
SP.append(plt.legend(loc=0))
plt.savefig("figures/ratio_plot_bechdel.png")
for s in SP: s.remove()


cmap = sns.color_palette("RdBu_r", 8)
colors = [cmap[x] for x in df["color"]]

S = plt.scatter(df[xkey].values, df[ykey].values,
                color=colors, **scatter_kwargs)


# Add custom legend
plt.scatter([],[],color=cmap[0],label="1920-1950",**scatter_kwargs)
plt.scatter([],[],color=cmap[4],label="1960-1980",**scatter_kwargs)
plt.scatter([],[],color=cmap[-1],label="1990-current",**scatter_kwargs)
plt.legend()

plt.savefig("figures/ratio_plot_years.png")

def draw_text(y_offset=0, fontsize=12):
    T = []
    for x,y,text in zip(df[xkey], df[ykey],df.index):

        # Clip long titles
        if len(text) > 15:
            text = text[:15] + '...'

        t = plt.text(x, y+y_offset, text, zorder=-2, fontsize=fontsize)
        t.set_bbox(dict(facecolor='white', alpha=0.5, edgecolor='white'))
        T.append(t)
    return T

T = draw_text(y_offset=0.015, fontsize=10)
plt.tight_layout()
plt.savefig("figures/ratio_plot_titles.png")

plt.show()
exit()

for t in T: t.remove()

plt.xlim(0, 0.05)
T = draw_text(y_offset=0.015, fontsize=16)
plt.tight_layout()
plt.savefig("figures/ratio_plot_males.png")
for t in T: t.remove()


plt.ylim(.6, 0.8)
plt.xlim(.5, 0.8)
T = draw_text(y_offset=0.005, fontsize=16)
plt.tight_layout()
plt.savefig("figures/ratio_plot_females.png")
#for t in T: t.remove()

plt.show()



