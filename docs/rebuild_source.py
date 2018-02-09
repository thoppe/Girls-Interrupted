import pandas as pd
import glob, os

F_MOVIE = glob.glob("../raw_videos/*")
F_MOVIE = map(os.path.basename, glob.glob("../raw_videos/*"))

cols = ['name', 'year','IMDB_rating']

df = pd.DataFrame()
df["source"] = F_MOVIE
df = df.set_index("source")

dfx = pd.read_csv("source_movies.csv")
dfx = dfx.set_index('source')

for col in cols:
    df[col] = dfx[col]

df.to_csv("source_movies.csv")

