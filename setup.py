# -*- encoding: utf-8 -*-

import os
from version import get_git_version
from setuptools import setup, find_packages


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='liquimigrate',
      version=get_git_version(),
      description="Liquibase migrations with django",
      long_description=(
          read('README.rst')
      ),
      classifiers=[
          'Programming Language :: Python',
        'Development Status :: 5 - Production/Stable',
      ],
      keywords='i-dotcom liquibase django',
      author='Marek Wywiał',
      author_email='marek.wywial@i-dotcom.pl',
      url="https://github.com/i-dotcom/liquimigrate",
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      test_suite='tests',
      include_package_data=True,
      zip_safe=False,
      install_requires=[
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
