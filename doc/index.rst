smbus2
======

.. image:: https://github.com/kplindegaard/smbus2/actions/workflows/python-build-test.yml/badge.svg?branch=master
   :target: https://github.com/kplindegaard/smbus2/actions/workflows/python-build-test.yml

.. image:: https://img.shields.io/pypi/pyversions/smbus2.svg
   :target: https://pypi.python.org/pypi/smbus2

.. image:: https://img.shields.io/pypi/v/smbus2.svg
   :target: https://pypi.python.org/pypi/smbus2

**smbus2** is a pure-Python, drop-in replacement for the ``python-smbus`` /
``python3-smbus`` Linux SMBus bindings. It wraps the Linux kernel's I2C/SMBus ``ioctl``
interface directly — no C extension required — and extends the familiar ``smbus`` API
with additional functionality such as combined read/write transactions (``i2c_rdwr``) and
Packet Error Checking (PEC).

.. code-block:: bash

   pip install smbus2

.. code-block:: python

   from smbus2 import SMBus

   with SMBus(1) as bus:
       value = bus.read_byte_data(0x50, 0)
       print(value)

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   introduction
   installation

.. toctree::
   :maxdepth: 2
   :caption: Using smbus2

   operations
   best_practices
   tips_and_tricks

.. toctree::
   :maxdepth: 2
   :caption: Support

   troubleshooting
   faq

.. toctree::
   :maxdepth: 2
   :caption: Reference

   api
   references
