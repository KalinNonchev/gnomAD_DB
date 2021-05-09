# gnomAD_MAF
[The Genome Aggregation Database (gnomAD)](https://gnomad.broadinstitute.org) is a resource developed by an international coalition of investigators, with the goal of aggregating and harmonizing both exome and genome sequencing data from a wide variety of large-scale sequencing projects, and making summary data available for the wider scientific community.

This package scales the huge gnomAD files (on average ~120G/chrom) to a SQLite database with a size of 56G for WGS v3.1.1 (about 760.000.000 variants), and allows scientists to look for minor allele frequencies of variants really fast (A query containing 300.000 variants takes ~40s.)

It extracts from a gnomAD vcf the ["AF", "AF_afr", "AF_eas", "AF_fin", "AF_nfe", "AF_asj", "AF_oth", "AF_popmax"] columns. 

###### The package works for all currently available gnomAD releases.(2021) 

## 1. Data preprocessing and SQL database creation

Start by downloading the vcf files from gnomAD in a single directory:

```bash
wget -c link_to_gnomAD.vcf.bgz
```

After that specify the arguments in the ```script_config.yaml```.
```
database_location: "test_out" # where to create the database, make sure you have space on your device.
gnomad_vcf_location: "data" # where are your *.vcf.bgz located
tables_location: "test_out" # where to store the preprocessed intermediate files, you can leave it like this 
script_locations: "test_out" # where to store the scripts, where you can check the progress of your jobs, you can leave it like this
```

Once this is done, run
```bash
conda env create -f environment.yaml
conda activate gnomad_db
python -m ipykernel install --user --name gnomad_db --display-name "gnomad_db"
```
to prepare your conda environment

Finally, you can trigger the snakemake pipeline which will create the SQL database
```bash
snakemake --cores 12
```

## 2. API usage

Congratulations, your database is set up! Now it is time to learn how to use it.

First, you can install the package in the gnomad_db env or in the one which you are going to use for your downstream analysis
```bash
pip install gnomad_db
```

You can use the package like

1. import modules
```python
import pandas as pd
from gnomad_db.database import gnomAD_DB
```

2. Initialize database connection
```python
# pass dir
database_location = "test_dir"
db = gnomAD_DB(database_location)
```

3. Insert some test variants to run the examples below
```python
# get some variants
var_df = pd.read_csv("data/test_vcf_gnomad_chr21_10000.tsv.gz", sep="\t", names=db.columns, index_col=False)
# IMPORTANT: The database removes internally chr prefix (chr1->1)
# insert these variants
db.insert_variants(var_df)
```

4. Query variant minor allele frequency
```python
# query some MAF scores
dummy_var_df = pd.DataFrame({
    "chrom": ["1", "21"], 
    "pos": [21, 9825790], 
    "ref": ["T", "C"], 
    "alt": ["G", "T"]})

# query from dataframe AF column
db.get_maf_from_df(dummy_var_df, "AF")

# query from dataframe AF and AF_popmax columns
db.get_maf_from_df(dummy_var_df, "AF, AF_popmax")

# query from dataframe all columns
db.get_maf_from_df(dummy_var_df, "*")

# query from string
db.get_maf_from_str("21:9825790:C>T", "AF")
```

5. You can query also intervals of minor allele frequencies
```python
db.get_mafs_for_interval(chrom=21, interval_start=9825780, interval_end=9825799, query="AF")
```

For more information on how to use the package, look into GettingStartedwithGnomAD_DB.ipynb notebook!

#### NB: The package is under development and any use cases suggestions/extensions and feedback are welcome.
