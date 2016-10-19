#!/usr/bin/env python

import sys
from setuptools import setup, find_packages

setup(
        author='Evan',
        url=' ',
	license=' ',
        platform='Python_2.7',
	description='WZS_project',
	keywords='WZS',
	author_email='evan@earlydata.com',
        name='WZS',
        version='1.0',
        packages=find_packages(),
        package_data={'':['*.rst','*.txt','*.md','*.sh','*.ipynb','*.csv','*.xls'],}
)



