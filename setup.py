
import os
from setuptools import setup, find_packages


__author__ = "Chen Kian Wee"
__copyright__ = "Copyright 2016, Chen Kian Wee"
__credits__ = ["Chen Kian Wee"]
__license__ = "MIT"
__version__ = "0.1a0"
__maintainer__ = "Chen Kian Wee"
__email__ = "chenkianwee@gmail.com"
__status__ = "Development"


with open('readme.txt', 'r') as f:
    LONG_DESCRIPTION = f.read()

INSTALL_REQUIRES = ['lxml', 'pyshp', 'pycollada', 'OCCUtils>=0.1-dev']


setup(name='pyliburo',
      version=__version__,
      description='Python Library for Urban Optimization',
      license='GPL3',
      author=__author__,
      author_email=__email__,
      url='https://github.com/chenkianwee/pyliburo',
      long_description=LONG_DESCRIPTION,
      py_modules=[''],
      packages=find_packages(),
      package_data={},
      dependency_links = ['https://github.com/tpaviot/pythonocc-utils/tarball/master#egg=OCCUtils-0.1-dev'],
      install_requires=INSTALL_REQUIRES,
      include_package_data=True,
      )
