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

# Clean IMDB URLS
func = lambda x:x.split('?')[0]
df["IMDB_url"] = df["IMDB_url"].apply(func)
    
# Extract the IMDB ID from the URL from those that don't have it
idx = pd.isnull(df["IMDB_ID"]) & (~pd.isnull(df["IMDB_url"]))
func = lambda x:int(x.split('/')[-2].strip('t'))
df.ix[idx, "IMDB_ID"] = df.ix[idx, "IMDB_url"].apply(func)

# Cross-reference data from https://shannonvturner.com/bechdel
f_shannon = "~/datasets/shannonvturnercom_bechdel_full.csv"
dfs = pd.read_csv(f_shannon).drop_duplicates(subset="imdb_id").set_index("imdb_id")

df["source"] = df.index
df = df.set_index("IMDB_ID")

# Only overwrite null values
replace_cols = [
    ["BECHDEL_rating","bechdel_rating"],
    ["IMDB_rating","imdb_rating"],
    ["RT_rating","tomato_meter"],
    ["RT_USER_rating","tomato_user_meter"],
]

for col1, col2 in replace_cols:
    idx = df.index[df[col1].isnull()]
    df.ix[idx, col1] = dfs.ix[idx, col2]


df.sort_values("year").to_csv("source_movies.csv")

