#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(name='pushlog',
      version='0.2.0',
      # Modules to import from other scripts:
      packages=find_packages(),
      # Executables
      scripts=["pushlog"],
     )
