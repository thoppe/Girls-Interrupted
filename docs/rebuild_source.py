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

for col in dfx.columns:
    df[col] = dfx[col]

# Extract the IMDB ID from the URL from those that don't have it
idx = pd.isnull(df["IMDB_ID"]) & (~pd.isnull(df["IMDB_url"]))
func = lambda x:int(x.split('/')[-2].strip('t'))
df.ix[idx, "IMDB_ID"] = df.ix[idx, "IMDB_url"].apply(func)

df.to_csv("source_movies.csv")

