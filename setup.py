#!/usr/bin/env python
from setuptools import setup, find_packages
from datetime import datetime #for version string
import os
import sys
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'neptune'))
import neptune

now = datetime.now()


#This will need to get fixed 
version="%s.%s.0a1" % (now.year, now.month) # PEP440 compliant

#note that this is only python2. fix later

setup(name="neptune",
      version=version,
      description="A C/C++ code navigator",
      url="https://github.com/jdukes/neptune",
      author="Josh Dukes",
      author_email="hex@neg9.org",
      license="MIT",
      entry_points = {
          'console_scripts': [
              'neptune_cc=neptune:neptune_cc',
              'neptune_cxx=neptune:neptune_cxx'
              ]
      },
      keywords = "C, C++, static analysis",
      long_description=neptune.__doc__,
      packages=find_packages())

