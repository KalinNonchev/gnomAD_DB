import urllib.request
import gzip
import shutil
from tqdm import tqdm
import os
import time


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_url(url, output_dir):
    with DownloadProgressBar(unit='B', unit_scale=True,
                             miniters=1, desc=url.split('/')[-1]) as t:
        urllib.request.urlretrieve(url, filename=f"{output_dir}/gnomad_db.sqlite3.gz", reporthook=t.update_to)
        time.sleep(5)

def unzip(output_dir):
    file_name_in = f"{output_dir}/gnomad_db.sqlite3.gz"
    file_name_out = f"{output_dir}/gnomad_db.sqlite3"
    with gzip.open(file_name_in, 'rb') as f_in:
        with open(file_name_out, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    time.sleep(5)
    os.remove(file_name_in)
    print(f"Database location: {file_name_out}")

def download_and_unzip_file(url, output_dir):
    print("Starting downloading...")
    download_url(url, output_dir)
    print("Starting unzipping. This can take some time...")
    unzip(output_dir)
    print("Done!")
    