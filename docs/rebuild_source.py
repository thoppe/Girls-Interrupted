import pandas as pd
import glob, os

F_MOVIE = glob.glob("../raw_videos/*")
F_MOVIE = map(os.path.basename, glob.glob("../raw_videos/*"))

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

# Cross-reference data from https://shannonvturner.com/bechdel
f_shannon = "~/datasets/shannonvturnercom_bechdel_full.csv"
dfs = pd.read_csv(f_shannon)
print dfs
exit()

df.to_csv("source_movies.csv")

