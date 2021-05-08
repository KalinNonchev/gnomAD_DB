from setuptools import setup, find_packages

setup(name='gnomad_db',
      version='0.0.2',
      description='This package scales the huge gnomAD files to a SQLite database, which is easy and fast to query. It extracts from a gnomAD vcf the minor allele frequency for each variants.',
      author='KalinNonchev',
      author_email='boo@foo.com',
      packages=find_packages(),  # find packages
      include_package_data=True,
      install_requires=['pandas', 'numpy']  # external packages as dependencies
      )
