###############################################################################
# Project: PLC Simulator
# Purpose: Packaging configuration for the PLC Simulator
# Author:  Paul M. Breen
# Date:    2018-07-31
###############################################################################

from setuptools import setup

setup(name='plc-simulator',
      version='0.3',
      description='PLC Simulator',
      url='https://github.com/paul-breen/plc-simulator',
      author='Paul Breen',
      author_email='paul.breen6@btinternet.com',
      license='Apache 2.0',
      packages=['plcsimulator'],
      scripts=['plc-simulator.py'],
      package_data={'plcsimulator': ['examples/*.json']})
