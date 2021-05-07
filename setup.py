from setuptools import setup, find_packages

setup(name='gnomad_db',
      version='0.0.1',
      description='Query gnomAD MAF',
      author='KalinNonchev',
      author_email='boo@foo.com',
      packages=find_packages(),  # find packages
      include_package_data=True,
      install_requires=['pandas', 'numpy']  # external packages as dependencies
      )
