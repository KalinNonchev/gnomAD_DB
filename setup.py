from setuptools import setup, find_packages

setup(name='gnomad_db',
      version='0.1.6',
      description='Scalable SQLite database for fast querying of gnomAD variant annotations (allele frequency, depth, population metrics)',
      author='Kalin Nonchev',
      license='MIT License',
      long_description_content_type='text/markdown',
      long_description=open('README.md').read(),
      url="https://github.com/KalinNonchev/gnomAD_DB",
      project_urls={
          "Bug Tracker": "https://github.com/KalinNonchev/gnomAD_DB/issues",
          "Pre-built Databases": "https://zenodo.org/records/11077663",
      },
      packages=find_packages(),
      package_data={
          "gnomad_db": ["pkgdata/*"],
      },
      include_package_data=True,
      install_requires=['pandas', 'numpy', 'joblib', 'tqdm', 'pyyaml'],
      python_requires='>=3.8',
      keywords=[
          'gnomad', 'genomics', 'bioinformatics', 'variant-annotation',
          'allele-frequency', 'sqlite', 'vcf', 'population-genetics',
      ],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
      ],
      )
