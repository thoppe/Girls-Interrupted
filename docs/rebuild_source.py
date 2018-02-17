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
# Replace '\N' null values with true nulls
for col in dfs.columns:
    if dfs[col].dtype in [str, object]:
        dfs[col] = dfs[col].str.replace(r'\N',"")

df["source"] = df.index
df = df.set_index("IMDB_ID")

df["BECHDEL_rating"] = dfs["bechdel_rating"]
df["IMDB_rating"] = dfs["imdb_rating"]
df["RT_rating"] = dfs["tomato_meter"]
df["RT_USER_rating"] = dfs["tomato_user_meter"]
df["runtime"] = dfs["runtime"]

df.sort_values("year").to_csv("source_movies.csv")

