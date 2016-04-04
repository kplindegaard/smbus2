from setuptools import setup

readme = """
Tullball
"""

setup(
    name="smbus2",
    version="0.1.0",
    author="Karl-Petter Lindegaard",
    author_email="kp.lindegaard@gmail.com",
    description="A drop-in replacement for smbus-cffi/smbus-python in pure Python",
    license="MIT",
    keywords= "smbus python i2c raspberrypi linux",
    url="https://github.com/kplindegaard/smbus2",
    packages=['smbus2'],
    long_description=readme,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)
