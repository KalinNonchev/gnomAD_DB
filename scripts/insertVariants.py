# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.10.2
#   kernelspec:
#     display_name: utr_anno
#     language: python
#     name: utr_anno
# ---

# %%
from gnomad_db.database import gnomAD_DB
import numpy as np
import pandas as pd
import gzip
from tqdm import tqdm
import glob

# %% tags=["parameters"]
database_location = "test"
tables_location = "test"

# %%
# initialize database
db = gnomAD_DB(database_location)

# %%
table_sep = "\t"


# %%
# read variants from tsv.gz table in batches
def load_batches(file, batch_size=500_000):
    with gzip.open(file, "rb") as f:
        batch = []
        for line in tqdm(f):
            line = line.decode().rstrip()
            if len(batch) == batch_size:
                batch = pd.DataFrame(batch, columns=db.columns).replace(".", np.NaN)
                yield batch
                batch = []

            batch.append(line.split(table_sep))
        
        
        if len(batch) != 0:
            batch = pd.DataFrame(batch, columns=db.columns).replace(".", np.NaN)
            yield batch

# %%
tables = glob.glob(f"{tables_location}/*.tsv.gz")
tables

# %%
for table in tables:
    print(table)
    for batch in load_batches(table):
        db.insert_variants(batch)

# %%
