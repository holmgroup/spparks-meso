from setuptools import setup
from Cython.Build import cythonize

setup(name='meso',
      version='0.1',
      description='Tools for working with polycrystalline microstructure models',
      url='tbd',
      author='Brian DeCost',
      author_email='bdecost@andrew.cmu.edu',
      license='MIT',
      packages=['meso'],
      zip_safe=False)
