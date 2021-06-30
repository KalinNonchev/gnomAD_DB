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


def download_url(url, output_path):
    with DownloadProgressBar(unit='B', unit_scale=True,
                             miniters=1, desc=url.split('/')[-1]) as t:
        urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)
        time.sleep(5)

def unzip(path_to_zip_file):
    file_name = path_to_zip_file.replace(".gz", "")
    with gzip.open(path_to_zip_file, 'rb') as f_in:
        with open(file_name, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    time.sleep(5)
    os.remove(path_to_zip_file)
    print(f"Database location: {file_name}")

def download_and_unzip_file(url, output_path):
    print("Starting downloading...")
    download_url(url, output_path)
    print("Starting unzipping. This can take some time...")
    unzip(output_path)
    print("Done!")
    