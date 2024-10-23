# The MIT License (MIT)
# Copyright (c) 2020 Karl-Petter Lindegaard
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

import sys
import unittest

try:
    import unittest.mock as mock
except ImportError:
    import mock  # noqa: F401

from smbus2 import SMBus, SMBusFreeBSD, i2c_msg, I2cFunc


##########################################################################
# Mock open, close and ioctl so we can run our unit tests anywhere.

# Required I2C constant definitions repeated
I2C_FUNCS = 0x0705  # Get the adapter functionality mask
I2C_SMBUS = 0x0720
I2C_SMBUS_WRITE = 0
I2C_SMBUS_READ = 1

I2C_SMBUS_QUICK = 0
I2C_SMBUS_BYTE_DATA = 2
I2C_SMBUS_WORD_DATA = 3
I2C_SMBUS_BLOCK_DATA = 5  # Can't get this one to work on my Raspberry Pi
I2C_SMBUS_I2C_BLOCK_DATA = 8
I2C_SMBUS_BLOCK_MAX = 32

MOCK_FD = "Mock file descriptor"

# Test buffer for read operations
test_buffer = [x for x in range(256)]


def bytes_six(lst):
    """convert a list of int to `bytes` like object"""
    if sys.version_info.major >= 3:
        return bytes(lst)
    else:
        return ''.join(map(chr, lst))


def mock_open(*args):
    print("Mocking open: %s" % args[0])
    return MOCK_FD


def mock_close(*args):
    print("Mocking close: %s" % args[0])
    assert args[0] == MOCK_FD


def mock_read(fd, length):
    assert fd == MOCK_FD
    return bytes_six(test_buffer[0:length])


def mock_ioctl(fd, command, msg):
    print("Mocking ioctl")
    assert fd == MOCK_FD
    assert command is not None

    # Reproduce i2c capability of a Raspberry Pi 3 w/o PEC support
    if command == I2C_FUNCS:
        msg.value = 0xeff0001
        return

    # Reproduce ioctl read operations
    if command == I2C_SMBUS and msg.read_write == I2C_SMBUS_READ:
        offset = msg.command
        if msg.size == I2C_SMBUS_BYTE_DATA:
            msg.data.contents.byte = test_buffer[offset]
        elif msg.size == I2C_SMBUS_WORD_DATA:
            msg.data.contents.word = test_buffer[offset + 1] * 256 + test_buffer[offset]
        elif msg.size == I2C_SMBUS_I2C_BLOCK_DATA:
            for k in range(msg.data.contents.byte):
                msg.data.contents.block[k + 1] = test_buffer[offset + k]

    # Reproduce a failing Quick write transaction
    if command == I2C_SMBUS and \
            msg.read_write == I2C_SMBUS_WRITE and \
            msg.size == I2C_SMBUS_QUICK:
        raise IOError("Mocking SMBus Quick failed")


# Mock platform.system function for Linux testing
def mock_get_system_linux():
    print('Mocking get_system() for Linux')
    return 'Linux'


# Mock platform.system functions for FreeBSD testing
def mock_get_system_freebsd():
    print('Mocking get_system() for FreeBSD')
    return 'FreeBSD'


# Mock platform.architecture functions for FreeBSD testing
def mock_get_arch():
    return ('64bit', 'ELF')


# Override open, close and ioctl with our mock functions
open_mock = mock.patch('smbus2.smbus2.os.open', mock_open)
close_mock = mock.patch('smbus2.smbus2.os.close', mock_close)
ioctl_mock = mock.patch('smbus2.smbus2.ioctl', mock_ioctl)
linux_system_mock = mock.patch('smbus2.smbus2.get_system', mock_get_system_linux)
freebsd_system_mock = mock.patch('smbus2.smbus2.get_system', mock_get_system_freebsd)
arch_mock = mock.patch('smbus2.smbus2.get_architecture', mock_get_arch)
##########################################################################

# Common error messages
INCORRECT_LENGTH_MSG = "Result array of incorrect length."


class SMBusTestCase(unittest.TestCase):
    def setUp(self):
        open_mock.start()
        close_mock.start()
        ioctl_mock.start()
        linux_system_mock.start()
        arch_mock.start()

    def tearDown(self):
        open_mock.stop()
        close_mock.stop()
        ioctl_mock.stop()
        linux_system_mock.stop()
        arch_mock.stop()


# Test cases
class TestSMBus(SMBusTestCase):
    def test_func(self):
        bus = SMBus(1)
        bus.open(1)
        print("\nSupported I2C functionality: %x" % bus.funcs)
        bus.close()

    def test_enter_exit(self):
        for id in (1, '/dev/i2c-alias'):
            with SMBus(id) as bus:
                self.assertIsNotNone(bus.fd)
            self.assertIsNone(bus.fd, None)

        with SMBus() as bus:
            self.assertIsNone(bus.fd)
            bus.open(2)
            self.assertIsNotNone(bus.fd)
        self.assertIsNone(bus.fd)

    def test_open_close(self):
        for id in (1, '/dev/i2c-alias'):
            bus = SMBus()
            self.assertIsNone(bus.fd)
            bus.open(id)
            self.assertIsNotNone(bus.fd)
            bus.close()
            self.assertIsNone(bus.fd)

    def test_read(self):
        res = []
        res2 = []
        res3 = []

        bus = SMBus(1)
        bus.open(1)

        # Read bytes
        for k in range(2):
            x = bus.read_byte_data(80, k)
            res.append(x)
        self.assertEqual(len(res), 2, msg=INCORRECT_LENGTH_MSG)

        # Read word
        x = bus.read_word_data(80, 0)
        res2.append(x & 255)
        res2.append(x / 256)
        self.assertEqual(len(res2), 2, msg=INCORRECT_LENGTH_MSG)
        self.assertListEqual(res, res2, msg="Byte and word reads differ")

        # Read block of N bytes
        n = 2
        x = bus.read_i2c_block_data(80, 0, n)
        res3.extend(x)
        self.assertEqual(len(res3), n, msg=INCORRECT_LENGTH_MSG)
        self.assertListEqual(res, res3, msg="Byte and block reads differ")

        bus.close()

    def test_quick(self):
        bus = SMBus(1)
        bus.open(1)
        self.assertRaises(IOError, bus.write_quick, 80)

    def test_pec(self):
        def set_pec(bus, enable=True):
            bus.pec = enable

        # Enabling PEC should fail (no mocked PEC support)
        bus = SMBus(1)
        bus.open(1)
        self.assertRaises(IOError, set_pec, bus, True)
        self.assertRaises(IOError, set_pec, bus, 1)
        self.assertEqual(bus.pec, 0)

        # Ensure PEC status is reset by close()
        bus._pec = 1
        self.assertEqual(bus.pec, 1)
        bus.close()
        self.assertEqual(bus.pec, 0)


class TestSMBusWrapper(SMBusTestCase):
    """Similar test as TestSMBus except it encapsulates it all access within "with" blocks."""

    def test_func(self):
        with SMBus(1) as bus:
            print("\nSupported I2C functionality: 0x%X" % bus.funcs)
            self.assertTrue(bus.funcs & I2cFunc.I2C > 0)
            self.assertTrue(bus.funcs & I2cFunc.SMBUS_QUICK > 0)

    def test_repeated_with(self):
        bus = SMBus(1)
        with bus:
            x = bus.read_i2c_block_data(80, 0, 2)
        self.assertEqual(len(x), 2, msg=INCORRECT_LENGTH_MSG)
        with bus:
            y = bus.read_i2c_block_data(80, 0, 2)
        self.assertEqual(x, y, msg="Results differ")

    def test_read(self):
        res = []
        res2 = []
        res3 = []

        # Read bytes
        with SMBus(1) as bus:
            for k in range(2):
                x = bus.read_byte_data(80, k)
                res.append(x)
        self.assertEqual(len(res), 2, msg=INCORRECT_LENGTH_MSG)

        # Read word
        with SMBus(1) as bus:
            x = bus.read_word_data(80, 0)
            res2.append(x & 255)
            res2.append(x / 256)
        self.assertEqual(len(res2), 2, msg=INCORRECT_LENGTH_MSG)
        self.assertListEqual(res, res2, msg="Byte and word reads differ")

        # Read block of N bytes
        n = 2
        with SMBus(1) as bus:
            x = bus.read_i2c_block_data(80, 0, n)
            res3.extend(x)
        self.assertEqual(len(res3), n, msg=INCORRECT_LENGTH_MSG)
        self.assertListEqual(res, res3, msg="Byte and block reads differ")


class TestI2CMsg(SMBusTestCase):
    def test_i2c_msg(self):
        # 1: Convert message content to list
        msg = i2c_msg.write(60, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        data = list(msg)
        self.assertEqual(len(data), 10)

        # 2: i2c_msg is iterable
        k = 0
        s = 0
        for value in msg:
            k += 1
            s += value
        self.assertEqual(k, 10, msg='Incorrect length')
        self.assertEqual(s, 55, msg='Incorrect sum')

        # 3: Through i2c_msg properties
        k = 0
        s = 0
        for k in range(msg.len):
            s += ord(msg.buf[k])
            k += 1
        self.assertEqual(k, 10, msg='Incorrect length')
        self.assertEqual(s, 55, msg='Incorrect sum')


# FreeBSD test cases
class SMBusFreeBSDTestCase(unittest.TestCase):
    def setUp(self):
        open_mock.start()
        close_mock.start()
        ioctl_mock.start()
        freebsd_system_mock.start()
        arch_mock.start()
        SMBus.system = None  # Reset OS detection

    def tearDown(self):
        open_mock.stop()
        close_mock.stop()
        ioctl_mock.stop()
        freebsd_system_mock.stop()
        arch_mock.stop()


class TestSMBusFreeBSD(SMBusFreeBSDTestCase):
    def test_freebsd_explicit(self):
        bus = SMBusFreeBSD(1)
        self.assertEqual(type(bus).__name__, 'SMBusFreeBSD')

    def test_freebsd_with(self):
        with SMBusFreeBSD(1) as bus:
            self.assertEqual(type(bus).__name__, 'SMBusFreeBSD')

    def test_freebsd_detected(self):
        with SMBus(1) as bus:
            self.assertTrue(bus.funcs & I2cFunc.I2C > 0)
            self.assertTrue(bus.funcs & I2cFunc.SMBUS_QUICK > 0)
            self.assertEqual(type(bus).__name__, 'SMBusFreeBSD')

    def test_freebsd_enter_exit(self):
        for id in (1, '/dev/i2c-alias'):
            with SMBus(id) as bus:
                self.assertEqual(type(bus).__name__, 'SMBusFreeBSD')
                self.assertIsNotNone(bus.fd)
            self.assertIsNone(bus.fd, None)

        with SMBus() as bus:
            self.assertEqual(type(bus).__name__, 'SMBusFreeBSD')
            self.assertIsNone(bus.fd)
            bus.open(2)
            self.assertIsNotNone(bus.fd)
        self.assertIsNone(bus.fd)
