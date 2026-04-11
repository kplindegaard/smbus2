# smbus2 Wiki

[![Build Status](https://github.com/kplindegaard/smbus2/actions/workflows/python-build-test.yml/badge.svg?branch=master)](https://github.com/kplindegaard/smbus2/actions/workflows/python-build-test.yml)
[![Documentation Status](https://readthedocs.org/projects/smbus2/badge/?version=latest)](http://smbus2.readthedocs.io/en/latest/?badge=latest)
[![PyPi Version](https://img.shields.io/pypi/v/smbus2.svg)](https://pypi.org/project/smbus2/)
![Python Versions](https://img.shields.io/pypi/pyversions/smbus2.svg)

**smbus2** is a pure-Python, drop-in replacement for the `python-smbus` / `python3-smbus` Linux SMBus bindings.
It wraps the Linux kernel's I2C/SMBus `ioctl` interface directly — no C extension required — and extends the
familiar `smbus` API with additional functionality such as combined read/write transactions (`i2c_rdwr`) and
Packet Error Checking (PEC).

Use the sidebar to navigate the wiki.

## Getting Started

```bash
pip install smbus2
```

```python
from smbus2 import SMBus

with SMBus(1) as bus:
    value = bus.read_byte_data(0x50, 0)
    print(value)
```

See [[Installation]] for system prerequisites and [[Operations]] for the full API reference.
