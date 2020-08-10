#!/usr/bin/env python

from setuptools import setup, find_packages
setup(
    name="klotio-python",
    version="0.2",
    package_dir = {'': 'lib'},
    py_modules = ['klotio_logger', 'klotio_unittest'],
    install_requires=[
        'python-json-logger==0.1.11',
        'PyYAML==5.3.1',
        'requests==2.24.0',
        'redis==3.5.2'
    ]
)
