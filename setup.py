from setuptools import setup, find_packages

setup(name='gnomad_db',
      version='0.1.0',
      description='This package scales the huge gnomAD files to a SQLite database, which is easy and fast to query. It extracts from a gnomAD vcf the minor allele frequency for each variant.',
      author='KalinNonchev',
      author_email='boo@foo.com',
      license='MIT License',
      long_description_content_type='text/markdown',
      long_description=open('README.md').read(),
      url="https://github.com/KalinNonchev/gnomAD_MAF",
      packages=find_packages(),  # find packages
      package_data={
          "gnomad_db": ["pkgdata/*"],   # include pkgdata into package
      },
      include_package_data=True,
      install_requires=['pandas', 'numpy', 'joblib', 'tqdm', 'pyyaml'],  # external packages as dependencies,
      python_requires='>=3.6'
      )
