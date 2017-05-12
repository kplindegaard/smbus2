# smbus2
A drop-in replacement for smbus-cffi/smbus-python in pure Python

[![Build Status](https://travis-ci.org/kplindegaard/smbus2.svg?branch=master)](https://travis-ci.org/kplindegaard/smbus2) 

# Introduction

smbus2 is (yet another) pure Python implementation of of the [python-smbus](http://www.lm-sensors.org/browser/i2c-tools/trunk/py-smbus/) package.

It was designed from the ground up with two goals in mind:

1. It should be a drop-in replacement of smbus. The syntax shall be the same.
2. Use the inherent i2c structs and unions to a greater extent than other pure Python implementations like [pysmbus](https://github.com/bjornt/pysmbus) does. By doing so, it will be more feature complete and easier to extend.

Currently supported features are:

* Get i2c capabilities (I2C_FUNCS)
* read_byte
* write_byte
* read_byte_data
* write_byte_data
* read_word_data
* write_word_data
* read_i2c_block_data
* write_i2c_block_data

It is developed on Python 2.7 but works without any modifications in Python 3.X too.

# Code examples

smbus2 installs next to smbus as the package, so it's not really a 100% replacement. You must change the module name.

## Example 1a: Read a byte

    from smbus2 import SMBus

    # Open i2c bus 1 and read one byte from address 80, offset 0
    bus = SMBus(1)
    b = bus.read_byte_data(80, 0)
    print(b)
    bus.close()
    
## Example 1b: Read a byte using 'with'

This is the very same example but safer to use since the smbus will be closed automatically when exiting the with block.

    from smbus2 import SMBusWrapper
    
    with SMBusWrapper(1) as bus:
        b = bus.read_byte_data(80, 0)
        print(b)

## Example 2: Read a block of data

You can read up to 32 bytes at once.

    from smbus2 import SMBusWrapper
    
    with SMBusWrapper(1) as bus:
        # Read a block of 16 bytes from address 80, offset 0
        block = bus.read_i2c_block_data(80, 0, 16)
        # Returned value is a list of 16 bytes
        print(block)

## Example 3: Write a byte

    from smbus2 import SMBusWrapper
    
    with SMBusWrapper(1) as bus:
        # Write a byte to address 80, offset 0
        data = 45
        bus.write_byte_data(80, 0, data)

## Example 4: Write a block of data

It is possible to write 32 bytes at the time, but I have found that error-prone. Write less and add a delay in between if you run into trouble.

    from smbus2 import SMBusWrapper
    
    with SMBusWrapper(1) as bus:
        # Write a block of 8 bytes to address 80 from offset 0
        data = [1, 2, 3, 4, 5, 6, 7, 8]
        bus.write_i2c_block_data(80, 0, data)

# Installation instructions

smbus2 is pure Python code and requires no compilation. Installation is easy:

    python setup.py install
    
Or just use pip

    pip install smbus2
