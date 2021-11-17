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

# %% papermill={"duration": 0.336842, "end_time": "2021-05-05T20:00:58.655105", "exception": false, "start_time": "2021-05-05T20:00:58.318263", "status": "completed"} tags=[]
import glob
from tqdm import tqdm
from subprocess import PIPE, Popen
import pandas as pd
from joblib import Parallel, delayed
import multiprocessing
import os
import yaml

# %% papermill={"duration": 0.336842, "end_time": "2021-05-05T20:00:58.655105", "exception": false, "start_time": "2021-05-05T20:00:58.318263", "status": "completed"} tags=[]
with open("gnomad_db/gnomad_columns.yaml") as f:
    columns = yaml.load(f, Loader=yaml.FullLoader)
columns = columns["base_columns"] + columns["value_columns"]
print(len(columns))
columns[:10]

# %% papermill={"duration": 0.014665, "end_time": "2021-05-05T20:00:58.675108", "exception": false, "start_time": "2021-05-05T20:00:58.660443", "status": "completed"} tags=["parameters"]
gnomad_vcf_location = "test"
tables_location = "test"

# %% papermill={"duration": 0.014665, "end_time": "2021-05-05T20:00:58.675108", "exception": false, "start_time": "2021-05-05T20:00:58.660443", "status": "completed"} tags=[]
# get gnomAD files
files = glob.glob(f"{gnomad_vcf_location}/*.bgz")
print(len(files))
files

# %% papermill={"duration": 0.008922, "end_time": "2021-05-05T20:00:58.701950", "exception": false, "start_time": "2021-05-05T20:00:58.693028", "status": "completed"} tags=[]
# write gnomAD files to these tables:
tables_location = [f'{tables_location}/{file.split("/")[-1].replace(".vcf.bgz", "")}.tsv.gz' for file in files]
tables_location

# %% papermill={"duration": 0.008863, "end_time": "2021-05-05T20:00:58.715794", "exception": false, "start_time": "2021-05-05T20:00:58.706931", "status": "completed"} tags=[]
cpu_count = int(multiprocessing.cpu_count())
cpu_count


# %% papermill={"duration": 0.008863, "end_time": "2021-05-05T20:00:58.715794", "exception": false, "start_time": "2021-05-05T20:00:58.706931", "status": "completed"} tags=[]
# extract needed columns
# if running DIRECTLY from notebook, add module load i12g/bcftools; in the beginning of cmd
def create_table(file, table_location):
    query_string = "%" + "\t%".join(columns) + "\n"
    
    if not os.path.exists(table_location):
        cmd = f"bcftools query -f '{query_string}' {file} | gzip > {table_location}"
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        print(p.communicate())
    


# %% papermill={"duration": 0.329741, "end_time": "2021-05-05T20:00:59.051392", "exception": false, "start_time": "2021-05-05T20:00:58.721651", "status": "completed"} tags=[]
# run bcftools in parallel
Parallel(cpu_count)(delayed(create_table)(file, table_location) for file, table_location in tqdm(zip(files, tables_location)))

# %%
