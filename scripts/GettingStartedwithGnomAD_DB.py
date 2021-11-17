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
import pandas as pd
import numpy as np

# %% [markdown]
# # Download SQLite preprocessed files
#
# I have preprocessed and created sqlite3 files for gnomAD v2.1.1 and 3.1.1 for you, which can be easily downloaded from here. They contain all variants on the 24 standard chromosomes.
#
# gnomAD v3.1.1 (hg38, 759'302'267 variants) 25G zipped, 56G in total - https://zenodo.org/record/5045170/files/gnomad_db_v3.1.1.sqlite3.gz?download=1 
# gnomAD v2.1.1 (hg19, 261'942'336 variants) 9G zipped, 20G in total - https://zenodo.org/record/5045102/files/gnomad_db_v2.1.1.sqlite3.gz?download=1 

# %%
# uncomment if you actually want to download it
# download_link = "https://zenodo.org/record/5045102/files/gnomad_db_v2.1.1.sqlite3.gz?download=1"
# output_dir = "test_dir" # database_location
# gnomAD_DB.download_and_unzip(download_link, output_dir) 

# %% [markdown]
# # Initialize Database

# %% tags=["parameters"]
# pass dir
database_location = "test_dir"

# %%
# initialize database
db = gnomAD_DB(database_location)

# %% [markdown]
# # Insert gnomAD variants into the database from single tsv file
# Look into insertVariants notebook to do it for big vcf files

# %%
# get some variants
var_df = pd.read_csv("data/test_vcf_gnomad_chr21_10000.tsv.gz", sep="\t", names=db.columns, index_col=False)
# preprocess missing values
# IMPORTANT: The database removes internally chr prefix (chr1->1)
var_df = var_df.replace(".", np.NaN)
var_df.head()

# %%
# insert variants
db.insert_variants(var_df)

# %% [markdown]
# # Query MAF

# %%
# check db columns, which we can query
db.columns

# %%
var_df = var_df[["chrom", "pos", "ref", "alt"]]
var_df.head()

# %% [markdown]
# ## You can pass a dataframe with variants
# It should contain the columns: [chrom, pos, ref, alt]

# %%
db.get_info_from_df(var_df, "AF").head() # only one columns

# %%
db.get_info_from_df(var_df, "AF, AF_popmax").head() # multiple columns

# %%
db.get_info_from_df(var_df, "*") # everything

# %%
dummy_var_df = pd.DataFrame({
    "chrom": ["1", "21"], 
    "pos": [21, 9825790], 
    "ref": ["T", "C"], 
    "alt": ["G", "T"]})
dummy_var_df

# %%
db.get_info_from_df(dummy_var_df, "AF")

# %% [markdown]
# ## You can pass a single string as a variant

# %%
db.get_info_from_str("21:9825790:C>T", "AF")

# %%
db.get_info_from_str("21:9825790:C>T", "*")

# %% [markdown]
# ## You can look for the MAF scores in an interval

# %%
db.get_info_for_interval(chrom=21, interval_start=9825780, interval_end=9825799, query="*")
