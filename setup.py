from setuptools import setup, find_packages

__author__ = "Chen Kian Wee"
__copyright__ = "Copyright 2016, Chen Kian Wee"
__credits__ = ["Chen Kian Wee"]
__license__ = "GPL3"
__version__ = "0.2"
__maintainer__ = "Chen Kian Wee"
__email__ = "chenkianwee@gmail.com"
__status__ = "Development"

LONG_DESCRIPTION = "refer to https://github.com/chenkianwee/py4design for full installation instructions"
    
INSTALL_REQUIRES = ['lxml', 'pyshp', 'numpy', 'pycollada', 'networkx', 'scikit-learn', 'pymf', 'cvxopt', 'matplotlib']

setup(name='py4design',
      packages = find_packages(),
      package_data={
          'py4design': ['databases/ettv/*.csv'],
		  'py4design': ['py2radiance/*.rad']
          },
      version=__version__,
      description='Python Library for Rapid Development of Bespoke Design Workflows',
      long_description=LONG_DESCRIPTION,
      author=__author__,
      author_email=__email__,
      url='https://github.com/chenkianwee/py4design',
      download_url = 'https://github.com/chenkianwee/pyliburo/archive/0.12a.tar.gz',
      keywords = ["urban design", "architecture design", "design optimisation", "design workflow", "design simulation"],
      install_requires=INSTALL_REQUIRES,
      classifiers = ['Development Status :: 3 - Alpha',
                     'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                     'Programming Language :: Python :: 2.7',],
      )
