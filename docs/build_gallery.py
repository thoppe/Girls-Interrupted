import pandas as pd
import glob, os

f_out = 'gallery_figures.md'
df = pd.read_csv("source_movies.csv").sort_values("year")

template = '''
**{name}**, _{year}_

![]({f_png})
'''.strip()+'\n'

S = []

for _,row in df.iterrows():

    f_png = os.path.join("..", "figures", row.source+'.png')
    if not os.path.exists(f_png):
        continue

    s = template.format(name=row['name'], year=row.year, f_png=f_png)
    S.append(s)

with open(f_out, 'w') as FOUT:
    FOUT.write('\n'.join(S))



