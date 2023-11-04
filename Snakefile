import glob
import yaml
import os

# -------------------------- READ CONFIG --------------------------

with open("script_config.yaml", 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

database_location = config['database_location']
gnomad_vcf_location = config['gnomad_vcf_location']
tables_location = config['tables_location']
script_locations = config['script_locations']
gnomad_version = config['gnomad_version']
KERNEL = config['KERNEL']


rule all:
    input:
        script_locations + "/scripts/insertVariants.ipynb"


# -------------------------- EXTRACT VARIANTS WITH MAF FROM gnomAD VCF --------------------------
rule extract_tables:
    input:
        notebook = "scripts/createTSVtables.ipynb"
    output:
        notebook = script_locations + "/scripts/createTSVtables.ipynb"
    message:
        "Running createTSVtables notebook..."
    shell:
        "papermill {input.notebook} {output.notebook} -p gnomad_vcf_location {gnomad_vcf_location} -p tables_location {tables_location} -p gnomad_version {gnomad_version} -k {KERNEL}"


# -------------------------- INSSERT VARIANTS WITH MAF TO DATABASE ------------------------------
rule insert_variants:
    input:
        script_locations + "/scripts/createTSVtables.ipynb",
        notebook = "scripts/insertVariants.ipynb"
    output:
        notebook = script_locations + "/scripts/insertVariants.ipynb"
    message:
        "Running insertVariants notebook..."
    shell:
        "papermill {input.notebook} {output.notebook} -p database_location {database_location} -p tables_location {tables_location} -p gnomad_version {gnomad_version} -k {KERNEL}"

# -------------------------- INSSERT VARIANTS WITH MAF TO DATABASE ------------------------------
#rule create_GettingStartedNB:
#    input:
#        script_locations + "/scripts/insertVariants.ipynb",
#        notebook = "scripts/GettingStartedwithGnomAD_DB.ipynb"
#    output:
#        notebook = script_locations + "/scripts/GettingStartedwithGnomAD_DB.ipynb"
#    message:
#        "Running GettingStartedwithGnomAD_DB notebook.... Take a look here!"
#    shell:
#        "papermill {input.notebook} {output.notebook} -p database_location {database_location} -k {KERNEL}"
