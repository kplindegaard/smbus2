from setuptools import setup
from os import path

# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), 'r') as f:
    readme = f.read()

setup(
    name="smbus2",
    version="0.1.5",
    author="Karl-Petter Lindegaard",
    author_email="kp.lindegaard@gmail.com",
    description="smbus2 is a drop-in replacement for smbus-cffi/smbus-python in pure Python",
    license="MIT",
    keywords=['smbus', 'smbus2', 'python', 'i2c', 'raspberrypi', 'linux'],
    url="https://github.com/kplindegaard/smbus2",
    packages=['smbus2'],
    long_description=readme,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3"
    ],
)
