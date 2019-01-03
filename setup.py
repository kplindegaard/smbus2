# The MIT License (MIT)
# Copyright (c) 2017 Karl-Petter Lindegaard

import re
import os
from io import open
from setuptools import setup


def read_file(fname, encoding='utf-8'):
    with open(fname, encoding=encoding) as r:
        return r.read()


def find_version(*file_paths):
    fpath = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = read_file(fpath)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)

    err_msg = 'Unable to find version string in {}'.format(fpath)
    raise RuntimeError(err_msg)


README = read_file('README.rst')
version = find_version('smbus2', '__init__.py')
test_deps = [
    'mock;python_version<"3.3"',
    'nose'
]

setup(
    name="smbus2",
    version=version,
    author="Karl-Petter Lindegaard",
    author_email="kp.lindegaard@gmail.com",
    description="smbus2 is a drop-in replacement for smbus-cffi/smbus-python in pure Python",
    license="MIT",
    keywords=['smbus', 'smbus2', 'python', 'i2c', 'raspberrypi', 'linux'],
    url="https://github.com/kplindegaard/smbus2",
    packages=['smbus2'],
    long_description=README,
    extras_require={
        'docs': [
            'sphinx >= 1.5.3'
        ],
        'qa': [
            'flake8'
        ],
        'test': test_deps
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
    ],
)
