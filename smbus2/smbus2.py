"""smbus2 - A drop-in replacement for smbus-cffi/smbus-python"""
# The MIT License (MIT)
# Copyright (c) 2017 Karl-Petter Lindegaard
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys
from fcntl import ioctl
from ctypes import c_uint32, c_uint8, c_uint16, c_char, POINTER, Structure, Array, Union, create_string_buffer


# Commands from uapi/linux/i2c-dev.h
I2C_SLAVE = 0x0703  # Use this slave address
I2C_SLAVE_FORCE = 0x0706  # Use this slave address, even if it is already in use by a driver!
I2C_FUNCS = 0x0705  # Get the adapter functionality mask
I2C_RDWR = 0x0707  # Combined R/W transfer (one STOP only)
I2C_SMBUS = 0x0720  # SMBus transfer. Takes pointer to i2c_smbus_ioctl_data

# SMBus transfer read or write markers from uapi/linux/i2c.h
I2C_SMBUS_WRITE = 0
I2C_SMBUS_READ = 1

# Size identifiers uapi/linux/i2c.h
I2C_SMBUS_BYTE = 1
I2C_SMBUS_BYTE_DATA = 2
I2C_SMBUS_WORD_DATA = 3
I2C_SMBUS_BLOCK_DATA = 5  # Can't get this one to work on my Raspberry Pi
I2C_SMBUS_I2C_BLOCK_DATA = 8
I2C_SMBUS_BLOCK_MAX = 32

# To determine what functionality is present (uapi/linux/i2c.h)
I2C_FUNC_I2C = 0x00000001
I2C_FUNC_10BIT_ADDR = 0x00000002
I2C_FUNC_PROTOCOL_MANGLING = 0x00000004  # I2C_M_IGNORE_NAK etc.
I2C_FUNC_SMBUS_PEC = 0x00000008
I2C_FUNC_NOSTART = 0x00000010  # I2C_M_NOSTART
I2C_FUNC_SLAVE = 0x00000020
I2C_FUNC_SMBUS_BLOCK_PROC_CALL = 0x00008000  # SMBus 2.0
I2C_FUNC_SMBUS_QUICK = 0x00010000
I2C_FUNC_SMBUS_READ_BYTE = 0x00020000
I2C_FUNC_SMBUS_WRITE_BYTE = 0x00040000
I2C_FUNC_SMBUS_READ_BYTE_DATA = 0x00080000
I2C_FUNC_SMBUS_WRITE_BYTE_DATA = 0x00100000
I2C_FUNC_SMBUS_READ_WORD_DATA = 0x00200000
I2C_FUNC_SMBUS_WRITE_WORD_DATA = 0x00400000
I2C_FUNC_SMBUS_PROC_CALL = 0x00800000
I2C_FUNC_SMBUS_READ_BLOCK_DATA = 0x01000000
I2C_FUNC_SMBUS_WRITE_BLOCK_DATA = 0x02000000
I2C_FUNC_SMBUS_READ_I2C_BLOCK = 0x04000000  # I2C-like block xfer
I2C_FUNC_SMBUS_WRITE_I2C_BLOCK = 0x08000000  # w/ 1-byte reg. addr.

# i2c_msg flags from uapi/linux/i2c.h
I2C_M_RD = 0x0001

# Pointer definitions
LP_c_uint8 = POINTER(c_uint8)
LP_c_uint16 = POINTER(c_uint16)
LP_c_uint32 = POINTER(c_uint32)


#############################################################
# Type definitions as in i2c.h


class i2c_smbus_data(Array):
    """
    Adaptation of the i2c_smbus_data union in ``i2c.h``.

    Data for SMBus messages.
    """
    _length_ = I2C_SMBUS_BLOCK_MAX + 2
    _type_ = c_uint8


class union_i2c_smbus_data(Union):
    _fields_ = [
        ("byte", c_uint8),
        ("word", c_uint16),
        ("block", i2c_smbus_data)
    ]


union_pointer_type = POINTER(union_i2c_smbus_data)


class i2c_smbus_ioctl_data(Structure):
    """
    As defined in ``i2c-dev.h``.
    """
    _fields_ = [
        ('read_write', c_uint8),
        ('command', c_uint8),
        ('size', c_uint32),
        ('data', union_pointer_type)]
    __slots__ = [name for name, type in _fields_]

    @staticmethod
    def create(read_write=I2C_SMBUS_READ, command=0, size=I2C_SMBUS_BYTE_DATA):
        u = union_i2c_smbus_data()
        return i2c_smbus_ioctl_data(
            read_write=read_write, command=command, size=size,
            data=union_pointer_type(u))


#############################################################
# Type definitions for i2c_rdwr combined transactions


class i2c_msg(Structure):
    """
    As defined in ``i2c.h``.
    """
    _fields_ = [
        ('addr', c_uint16),
        ('flags', c_uint16),
        ('len', c_uint16),
        ('buf', POINTER(c_char))]
    __slots__ = [name for name, type in _fields_]

    def __iter__(self):
        return i2c_msg_iter(self)

    @staticmethod
    def read(address, length):
        """
        Prepares an i2c read transaction.

        :param address: Slave address.
        :type: address: int
        :param length: Number of bytes to read.
        :type: length: int
        :return: New :py:class:`i2c_msg` instance for read operation.
        :rtype: :py:class:`i2c_msg`
        """
        arr = create_string_buffer(length)
        return i2c_msg(
            addr=address, flags=I2C_M_RD, len=length,
            buf=arr)

    @staticmethod
    def write(address, buf):
        """
        Prepares an i2c write transaction.

        :param address: Slave address.
        :type address: int
        :param buf: Bytes to write. Either list of values or str.
        :type buf: list
        :return: New :py:class:`i2c_msg` instance for write operation.
        :rtype: :py:class:`i2c_msg`
        """
        if sys.version_info.major >= 3:
            if type(buf) is str:
                buf = bytes(buf, 'UTF-8')
            else:
                buf = bytes(buf)
        else:
            if type(buf) is not str:
                buf = ''.join([chr(x) for x in buf])
        arr = create_string_buffer(buf, len(buf))
        return i2c_msg(
            addr=address, flags=0, len=len(arr),
            buf=arr)


class i2c_rdwr_ioctl_data(Structure):
    """
    As defined in ``i2c-dev.h``.
    """
    _fields_ = [
        ('msgs', POINTER(i2c_msg)),
        ('nmsgs', c_uint32)
    ]
    __slots__ = [name for name, type in _fields_]

    @staticmethod
    def create(*i2c_msg_instances):
        """
        Factory method for creating a i2c_rdwr_ioctl_data struct that can
        be called with ``ioctl(fd, I2C_RDWR, data)``.

        :param i2c_msg_instances: Up to 42 i2c_msg instances
        :rtype: i2c_rdwr_ioctl_data
        """
        n_msg = len(i2c_msg_instances)
        msg_array = (i2c_msg * n_msg)(*i2c_msg_instances)
        return i2c_rdwr_ioctl_data(
            msgs=msg_array,
            nmsgs=n_msg
        )


class i2c_msg_iter:
    """
    :py:class:`i2c_msg` iterator. For convenience.
    """

    def __init__(self, msg):
        self.msg = msg
        self.idx = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.idx < self.msg.len:
            val = ord(self.msg.buf[self.idx])
            self.idx += 1
            return val
        else:
            raise StopIteration()

    def next(self):
        return self.__next__()

#############################################################


class SMBus(object):

    def __init__(self, bus=None, force=False):
        """
        Initialize and (optionally) open an i2c bus connection.

        :param bus: i2c bus number (e.g. 0 or 1). If not given, a subsequent
            call to ``open()`` is required.
        :type bus: int
        :param force: force using the slave address even when driver is
            already using it.
        :type force: boolean
        """
        self.fd = None
        self.funcs = 0
        if bus is not None:
            self.open(bus)
        self.address = None
        self.force = force
        self._force_last = None

    def open(self, bus):
        """
        Open a given i2c bus.

        :param bus: i2c bus number (e.g. 0 or 1)
        :type bus: int
        """
        self.fd = os.open("/dev/i2c-{}".format(bus), os.O_RDWR)
        self.funcs = self._get_funcs()

    def close(self):
        """
        Close the i2c connection.
        """
        if self.fd:
            os.close(self.fd)
            self.fd = None

    def _set_address(self, address, force=None):
        """
        Set i2c slave address to use for subsequent calls.

        :param address:
        :type address: int
        :param force:
        :type force: Boolean
        """
        force = force if force is not None else self.force
        if self.address != address or self._force_last != force:
            if force is True:
                ioctl(self.fd, I2C_SLAVE_FORCE, address)
            else:
                ioctl(self.fd, I2C_SLAVE, address)
            self.address = address
            self._force_last = force

    def _get_funcs(self):
        """
        Returns a 32-bit value stating supported I2C functions.

        :rtype: int
        """
        f = c_uint32()
        ioctl(self.fd, I2C_FUNCS, f)
        return f.value

    def read_byte(self, i2c_addr, force=None):
        """
        Read a single byte from a device.

        :rtype: int
        :param i2c_addr: i2c address
        :type i2c_addr: int
        :param force:
        :type force: Boolean
        :return: Read byte value
        """
        self._set_address(i2c_addr, force=force)
        msg = i2c_smbus_ioctl_data.create(
            read_write=I2C_SMBUS_READ, command=0, size=I2C_SMBUS_BYTE
        )
        ioctl(self.fd, I2C_SMBUS, msg)
        return msg.data.contents.byte

    def write_byte(self, i2c_addr, value, force=None):
        """
        Write a single byte to a device.

        :param i2c_addr: i2c address
        :type i2c_addr: int
        :param value: value to write
        :type value: int
        :param force:
        :type force: Boolean
        """
        self._set_address(i2c_addr, force=force)
        msg = i2c_smbus_ioctl_data.create(
            read_write=I2C_SMBUS_WRITE, command=value, size=I2C_SMBUS_BYTE
        )
        ioctl(self.fd, I2C_SMBUS, msg)

    def read_byte_data(self, i2c_addr, register, force=None):
        """
        Read a single byte from a designated register.

        :param i2c_addr: i2c address
        :type i2c_addr: int
        :param register: Register to read
        :type register: int
        :param force:
        :type force: Boolean
        :return: Read byte value
        :rtype: int
        """
        self._set_address(i2c_addr, force=force)
        msg = i2c_smbus_ioctl_data.create(
            read_write=I2C_SMBUS_READ, command=register, size=I2C_SMBUS_BYTE_DATA
        )
        ioctl(self.fd, I2C_SMBUS, msg)
        return msg.data.contents.byte

    def write_byte_data(self, i2c_addr, register, value, force=None):
        """
        Write a byte to a given register.

        :param i2c_addr: i2c address
        :type i2c_addr: int
        :param register: Register to write to
        :type register: int
        :param value: Byte value to transmit
        :type value: int
        :param force:
        :type force: Boolean
        :rtype: None
        """
        self._set_address(i2c_addr, force=force)
        msg = i2c_smbus_ioctl_data.create(
            read_write=I2C_SMBUS_WRITE, command=register, size=I2C_SMBUS_BYTE_DATA
        )
        msg.data.contents.byte = value
        ioctl(self.fd, I2C_SMBUS, msg)

    def read_word_data(self, i2c_addr, register, force=None):
        """
        Read a single word (2 bytes) from a given register.

        :param i2c_addr: i2c address
        :type i2c_addr: int
        :param register: Register to read
        :type register: int
        :param force:
        :type force: Boolean
        :return: 2-byte word
        :rtype: int
        """
        self._set_address(i2c_addr, force=force)
        msg = i2c_smbus_ioctl_data.create(
            read_write=I2C_SMBUS_READ, command=register, size=I2C_SMBUS_WORD_DATA
        )
        ioctl(self.fd, I2C_SMBUS, msg)
        return msg.data.contents.word

    def write_word_data(self, i2c_addr, register, value, force=None):
        """
        Write a byte to a given register.

        :param i2c_addr: i2c address
        :type i2c_addr: int
        :param register: Register to write to
        :type register: int
        :param value: Word value to transmit
        :type value: int
        :param force:
        :type force: Boolean
        :rtype: None
        """
        self._set_address(i2c_addr, force=force)
        msg = i2c_smbus_ioctl_data.create(
            read_write=I2C_SMBUS_WRITE, command=register, size=I2C_SMBUS_WORD_DATA
        )
        msg.data.contents.word = value
        ioctl(self.fd, I2C_SMBUS, msg)

    def read_i2c_block_data(self, i2c_addr, register, length, force=None):
        """
        Read a block of byte data from a given register.

        :param i2c_addr: i2c address
        :type i2c_addr: int
        :param register: Start register
        :type register: int
        :param length: Desired block length
        :type length: int
        :param force:
        :type force: Boolean
        :return: List of bytes
        :rtype: list
        """
        if length > I2C_SMBUS_BLOCK_MAX:
            raise ValueError("Desired block length over %d bytes" % I2C_SMBUS_BLOCK_MAX)
        self._set_address(i2c_addr, force=force)
        msg = i2c_smbus_ioctl_data.create(
            read_write=I2C_SMBUS_READ, command=register, size=I2C_SMBUS_I2C_BLOCK_DATA
        )
        msg.data.contents.byte = length
        ioctl(self.fd, I2C_SMBUS, msg)
        return msg.data.contents.block[1:length + 1]

    def write_i2c_block_data(self, i2c_addr, register, data, force=None):
        """
        Write a block of byte data to a given register.

        :param i2c_addr: i2c address
        :type i2c_addr: int
        :param register: Start register
        :type register: int
        :param data: List of bytes
        :type data: list
        :param force:
        :type force: Boolean
        :rtype: None
        """
        length = len(data)
        if length > I2C_SMBUS_BLOCK_MAX:
            raise ValueError("Data length cannot exceed %d bytes" % I2C_SMBUS_BLOCK_MAX)
        self._set_address(i2c_addr, force=force)
        msg = i2c_smbus_ioctl_data.create(
            read_write=I2C_SMBUS_WRITE, command=register, size=I2C_SMBUS_I2C_BLOCK_DATA
        )
        msg.data.contents.block[0] = length
        msg.data.contents.block[1:length + 1] = data
        ioctl(self.fd, I2C_SMBUS, msg)

    def i2c_rdwr(self, *i2c_msgs):
        """
        Combine a series of i2c read and write operations in a single
        transaction (with repeted start bits but no stop bits in between).

        This method takes i2c_msg instances as input, which must be created
        first with :py:meth:`i2c_msg.read` or :py:meth:`i2c_msg.write`.

        :param i2c_msgs: One or more i2c_msg class instances.
        :type i2c_msgs: i2c_msg
        :rtype: None
        """
        ioctl_data = i2c_rdwr_ioctl_data.create(*i2c_msgs)
        ioctl(self.fd, I2C_RDWR, ioctl_data)


class SMBusWrapper:
    """
    Wrapper class around the SMBus.

    Enables the user to wrap access to the :py:class:`SMBus` class in a
    "with" statement. If auto_cleanup is True (default), the
    :py:class:`SMBus` handle will be automatically closed
    upon exit of the ``with`` block.
    """
    def __init__(self, bus_number=0, auto_cleanup=True, force=False):
        """
        :param auto_cleanup: Close bus when leaving scope.
        :type auto_cleanup: Boolean
        :param force: Force using the slave address even when driver is already using it.
        :type force: Boolean
        """
        self.bus_number = bus_number
        self.auto_cleanup = auto_cleanup
        self.force = force

    def __enter__(self):
        self.bus = SMBus(bus=self.bus_number, force=self.force)
        return self.bus

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.auto_cleanup:
            self.bus.close()
