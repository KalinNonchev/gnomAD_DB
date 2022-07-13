# gnomAD_DB

### Changelog

#### NEW version (July 2022)
- release gnomAD WGS v3.1.2
- minor bug fixes

#### version (December 2021)
- more available variant features present, check [here](https://github.com/KalinNonchev/gnomAD_DB/blob/master/gnomad_db/pkgdata/gnomad_columns.yaml)
- `get_maf_from_df` renamed to `get_info_from_df`
- `get_maf_from_str` renamed to `get_info_from_str`
- `genome`=["Grch37"|"Grch38"] argument have to be specified, when initializing the database


[The Genome Aggregation Database (gnomAD)](https://gnomad.broadinstitute.org) is a resource developed by an international coalition of investigators, with the goal of aggregating and harmonizing both exome and genome sequencing data from a wide variety of large-scale sequencing projects, and making summary data available for the wider scientific community.

This package scales the huge gnomAD files (on average ~120G/chrom) to a SQLite database with a size of 34G for WGS v2.1.1 (261.942.336 variants) and 98G for WGS v3.1.2 (about 759.302.267 variants), and allows scientists to look for various variant annotations present in gnomAD (i.e. Allele Count, Depth, Minor Allele Frequency, etc. - [here](https://github.com/KalinNonchev/gnomAD_DB/blob/master/gnomad_db/pkgdata/gnomad_columns.yaml) you can find all selected features given the genome version). (A query containing 300.000 variants takes ~40s.)

It extracts from a gnomAD vcf about 23 variant annotations. You can find further infromation about the exact fields [here](https://github.com/KalinNonchev/gnomAD_DB/blob/master/gnomad_db/pkgdata/gnomad_columns.yaml). 

###### The package works for all currently available gnomAD releases.(July 2022) 

## 1. Download SQLite preprocessed files

I have preprocessed and created sqlite3 files for gnomAD v2.1.1 and 3.1.2 for you, which can be easily downloaded from here. They contain all variants on the 24 standard chromosomes.

gnomAD v3.1.2 (hg38, **759'302'267** variants) 46.2G zipped, 98G in total - https://zenodo.org/record/6818606/files/gnomad_db_v3.1.2.sqlite3.gz?download=1 \
gnomAD v2.1.1 (hg19, **261'942'336** variants) 16.1G zipped, 48G in total - https://zenodo.org/record/5770384/files/gnomad_db_v2.1.1.sqlite3.gz?download=1

You can download it as:

```python
from gnomad_db.database import gnomAD_DB
download_link = "https://zenodo.org/record/6818606/files/gnomad_db_v3.1.2.sqlite3.gz?download=1"
output_dir = "test_dir" # database_location
gnomAD_DB.download_and_unzip(download_link, output_dir)
```
#### NB this would take ~30min (network speed 10mb/s)


or you can create the database by yourself. **However, I recommend to use the preprocessed files to save ressources and time**. If you do so, you can go to **2. API usage** and explore the package and its great features!


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

2. Initialize database connection \
**Make sure to have the correct genome version!**
```python
# pass dir
database_location = "test_dir"
db = gnomAD_DB(database_location, genome="Grch38")
```

3. Insert some test variants to run the examples below \
**If you have downloaded the preprocessed sqlite3 files, you can skip this step as you already have variants, make sure to have the correct genome version!**
```python
# get some variants
var_df = pd.read_csv("data/test_vcf_gnomad_chr21_10000.tsv.gz", sep="\t", names=db.columns, index_col=False)
# IMPORTANT: The database removes internally chr prefix (chr1->1)
# insert these variants
db.insert_variants(var_df)
```

4. Query variant minor allele frequency \
**These example variants are assembled to hg38!**
```python
# query some MAF scores
dummy_var_df = pd.DataFrame({
    "chrom": ["1", "21"], 
    "pos": [21, 9825790], 
    "ref": ["T", "C"], 
    "alt": ["G", "T"]})

# query from dataframe AF column
db.get_info_from_df(dummy_var_df, "AF")

# query from dataframe AF and AF_popmax columns
db.get_info_from_df(dummy_var_df, "AF, AF_popmax")

# query from dataframe all columns
db.get_info_from_df(dummy_var_df, "*")

# query from string
db.get_info_from_str("21:9825790:C>T", "AF")
```

5. You can query also intervals of minor allele frequencies
```python
db.get_info_for_interval(chrom=21, interval_start=9825780, interval_end=9825799, query="AF")
```

For more information on how to use the package, look into GettingStartedwithGnomAD_DB.ipynb notebook!
#### NB: The package is under development and any use cases suggestions/extensions and feedback are welcome.
