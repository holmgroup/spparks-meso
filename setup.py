from setuptools import setup, find_packages
from Cython.Build import cythonize

setup(name='meso',
      version='0.1',
      description='Tools for working with polycrystalline microstructure models',
      url='tbd',
      author='Brian DeCost',
      author_email='bdecost@andrew.cmu.edu',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
          'numpy',
          'scipy',
          'h5py',
          'networkx',
          'scikit-image',
          'click'
      ],
      entry_points='''
      [console_scripts]
      meso=meso.scripts.cli:cli
      ''',
)
