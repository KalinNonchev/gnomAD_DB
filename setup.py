from setuptools import setup, find_packages

setup(name='gnomad_db',
      version='0.0.0',
      description='Query gnomAD MAF',
      author='KalinNonchev',
      author_email='boo@foo.com',
      packages=find_packages(),  # find packages
      include_package_data=True,
      install_requires=['pandas', 'numpy', 'pysqlite3']  # external packages as dependencies
      )
