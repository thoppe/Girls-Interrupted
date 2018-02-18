import pandas as pd
import glob, os, json

F_MOVIE = glob.glob("../raw_videos/*")
F_MOVIE = map(os.path.basename, glob.glob("../raw_videos/*"))

df = pd.DataFrame()
df["source"] = F_MOVIE
df = df.set_index("source")

dfx = pd.read_csv("source_movies.csv")
dfx = dfx.set_index('source')

for col in dfx.columns:
    df[col] = dfx[col]

'''
# Clean IMDB URLS
df.ix[pd.isnull(df.IMDB_url), "IMDB_url"] = ""
func = lambda x:x.split('?')[0]
df["IMDB_url"] = df["IMDB_url"].astype(str).apply(func)
    
# Extract the IMDB ID from the URL from those that don't have it
idx = pd.isnull(df["IMDB_ID"]) & (~pd.isnull(df["IMDB_url"]))
idx = idx & (df.IMDB_url!='')
func = lambda x:int(x.split('/')[-2].strip('t'))
df.ix[idx, "IMDB_ID"] = df.ix[idx, "IMDB_url"].apply(func)
print df.IMDB_ID.values
exit()
'''

# Fill in missing IMDB_IDs
idx = pd.isnull(df.IMDB_ID)
df.ix[idx, 'IMDB_ID'] = df.index[idx]


# Cross-reference data from https://shannonvturner.com/bechdel
f_shannon = "~/datasets/shannonvturnercom_bechdel_full.csv"
dfs = pd.read_csv(f_shannon).drop_duplicates(subset="imdb_id").set_index("imdb_id")

df["source"] = df.index
df = df.set_index("IMDB_ID")

# Only overwrite null values
replace_cols = [
    ["BECHDEL_rating","bechdel_rating"],
    ["IMDB_rating","imdb_rating"],
]

for col1, col2 in replace_cols:
    idx = df.index[df[col1].isnull()]
    df.ix[idx, col1] = dfs.ix[idx, col2]


# Gather information about the movies from the summary
for f_json in glob.glob("../data/summary/*.json"):
    with open(f_json) as FIN:
        js = json.loads(FIN.read())
    source = os.path.basename(js.pop('f_movie'))

    if (df.source==source).sum() != 1:
        print "Weirdness with movie", f_json
        continue

    continue
    exit()



df.sort_values("year").to_csv("source_movies.csv")

