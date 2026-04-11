# smbus2 Wiki

[![Build Status](https://github.com/kplindegaard/smbus2/actions/workflows/python-build-test.yml/badge.svg?branch=master)](https://github.com/kplindegaard/smbus2/actions/workflows/python-build-test.yml)
[![Documentation Status](https://readthedocs.org/projects/smbus2/badge/?version=latest)](http://smbus2.readthedocs.io/en/latest/?badge=latest)
[![PyPi Version](https://img.shields.io/pypi/v/smbus2.svg)](https://pypi.org/project/smbus2/)
![Python Versions](https://img.shields.io/pypi/pyversions/smbus2.svg)

**smbus2** is a pure-Python, drop-in replacement for the `python-smbus` / `python3-smbus` Linux SMBus bindings.
It wraps the Linux kernel's I2C/SMBus `ioctl` interface directly — no C extension required — and extends the
familiar `smbus` API with additional functionality such as combined read/write transactions (`i2c_rdwr`) and
Packet Error Checking (PEC).

## Quick Navigation

| Page | Description |
|------|-------------|
| [[Introduction]] | What smbus2 does, platform support, supported operations |
| [[Installation]] | pip, conda, source install and system prerequisites |
| [[Operations]] | Full API reference with code examples |
| [[Best Practices]] | Patterns for reliable, maintainable I2C code |
| [[Tips and Tricks]] | Community-sourced recipes for common tasks |
| [[Troubleshooting]] | Diagnosing runtime errors by error type |
| [[FAQ]] | Short answers to frequently asked questions |

## Getting Started

Install from PyPI and open a bus in three lines:

```python
pip install smbus2
```

```python
from smbus2 import SMBus

with SMBus(1) as bus:
    value = bus.read_byte_data(0x50, 0)
    print(value)
```

See [[Operations]] for the full API and [[Installation]] for system prerequisites.
