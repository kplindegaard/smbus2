# smbus2

[![](https://img.shields.io/badge/GitHub-kplindegaard%2Fsmbus2-blue?logo=github)](https://github.com/kplindegaard/smbus2)
[![](https://github.com/kplindegaard/smbus2/actions/workflows/python-build-test.yml/badge.svg?branch=master)](https://github.com/kplindegaard/smbus2/actions/workflows/python-build-test.yml)
[![](https://github.com/kplindegaard/smbus2/actions/workflows/codeql-analysis.yml/badge.svg?branch=master)](https://github.com/kplindegaard/smbus2/actions/workflows/codeql-analysis.yml)
[![](https://readthedocs.org/projects/smbus2/badge/?version=latest)](http://smbus2.readthedocs.io/en/latest/?badge=latest)
[![](https://img.shields.io/pypi/pyversions/smbus2.svg)](https://pypi.python.org/pypi/smbus2)
[![](https://img.shields.io/pypi/v/smbus2.svg)](https://pypi.python.org/pypi/smbus2)

**smbus2** is a pure-Python, drop-in replacement for the `python-smbus` /
`python3-smbus` Linux SMBus bindings. It wraps the Linux kernel's I2C/SMBus `ioctl`
interface directly — no C extension required — and extends the familiar `smbus` API
with additional functionality such as combined read/write transactions (`i2c_rdwr`) and
Packet Error Checking (PEC).

```{toctree}
:maxdepth: 2
:caption: Getting Started

introduction
installation
```

```{toctree}
:maxdepth: 2
:caption: Using smbus2

operations
best_practices
tips_and_tricks
```

```{toctree}
:maxdepth: 2
:caption: Support

troubleshooting
faq
```

```{toctree}
:maxdepth: 2
:caption: Reference

api
references
```
