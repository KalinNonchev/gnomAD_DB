## Data preprocessing and SQL database creation

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
genome: "Grch37" # genome version of the gnomAD vcf file (2.1.1 = Grch37, 3.1.1 = Grch38)
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
