#!/bin/bash

base_url="https://storage.googleapis.com/gcp-public-data--gnomad/release/4.0/vcf/genomes/gnomad.genomes.v4.0.sites.chr"

# Function to download a pair of bgz and tbi files
download_files() {
    local url="$1"
    wget -c "$url.vcf.bgz" &&
    wget -c "$url.vcf.bgz.tbi"
}

# Loop through chromosomes 1 to 22
for i in {1..22}; do
    download_files "${base_url}${i}" &
done

# Additional chromosomes X and Y
download_files "${base_url}X" &
download_files "${base_url}Y" &

# Wait for all background jobs to finish
wait

# Function to check integrity using bgzip -t
check_integrity() {
    local file="$1"
    if bgzip -t "$file"; then
        echo "$file is verified successfully."
    else
        echo "Error: $file is corrupted!"
    fi
}

# Check the integrity using bgzip -t for all .vcf.bgz files in the current directory in parallel
for file in *.vcf.bgz; do
    if [[ -e "$file" ]]; then
        check_integrity "$file" &
    fi
done

# Wait for all background integrity check jobs to finish
wait

