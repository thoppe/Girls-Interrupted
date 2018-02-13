import pandas as pd
import glob, os

f_out = 'gallery_figures.md'
df = pd.read_csv("source_movies.csv").sort_values("year")

template = '''
**{name}**, _{year}_

![]({f_png})
'''.strip()+'\n'

S = ['''## {} movies profiled\n'''.format(len(df))]

for _,row in df.iterrows():

    f_png = os.path.join("..", "figures", "lineplots", row.source+'.png')
    if not os.path.exists(f_png):
        continue

    #print f_png

    s = template.format(
        name=row['name'],
        year=row.year,
        f_png=f_png.replace(' ', '%20'),
    )
    S.append(s)

with open(f_out, 'w') as FOUT:
    FOUT.write('\n'.join(S))
