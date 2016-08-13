# The MIT License (MIT)
# Copyright (c) 2016 Karl-Petter Lindegaard
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

from smbus2 import SMBus, SMBusWrapper
import unittest

try:
    import mock
except ImportError:
    import unittest.mock as mock


##########################################################################
# Mock open, close and ioctl so we can run our unit tests anywhere.

# Required I2C constant definitions repeated
I2C_SMBUS = 0x0720
I2C_SMBUS_READ = 1
I2C_SMBUS_BYTE_DATA = 2
I2C_SMBUS_WORD_DATA = 3
I2C_SMBUS_BLOCK_DATA = 5  # Can't get this one to work on my Raspberry Pi
I2C_SMBUS_I2C_BLOCK_DATA = 8
I2C_SMBUS_BLOCK_MAX = 32

MOCK_FD = "Mock file descriptor"

# Test buffer for read operations
test_buffer = [x for x in range(256)]


def mock_open(*args):
    print("Mocking open: %s" % args[0])
    return MOCK_FD


def mock_close(*args):
    assert args[0] == MOCK_FD


def mock_ioctl(fd, command, msg):
    print("Mocking ioctl")
    assert fd == MOCK_FD
    assert command is not None

    # Reproduce ioctl read operations
    if command == I2C_SMBUS and msg.read_write == I2C_SMBUS_READ:
        offset = msg.command
        if msg.size == I2C_SMBUS_BYTE_DATA:
            msg.data.contents.byte = test_buffer[offset]
        elif msg.size == I2C_SMBUS_WORD_DATA:
            msg.data.contents.word = test_buffer[offset+1]*256 + test_buffer[offset]
        elif msg.size == I2C_SMBUS_I2C_BLOCK_DATA:
            for k in range(msg.data.contents.byte):
                msg.data.contents.block[k+1] = test_buffer[offset+k]

# Override open, close and ioctl with our mock functions
open_mock = mock.patch('smbus2.smbus2.os.open', mock_open)
close_mock = mock.patch('smbus2.smbus2.os.close', mock_close)
ioctl_mock = mock.patch('smbus2.smbus2.ioctl', mock_ioctl)
open_mock.start()
close_mock.start()
ioctl_mock.start()
##########################################################################


# Test cases
class TestSMBus(unittest.TestCase):
    def test_func(self):
        bus = SMBus(1)
        print("\nSupported I2C functionality: %x" % bus.funcs)
        bus.close()

    def test_read(self):
        res = []
        res2 = []
        res3 = []

        bus = SMBus(1)

        # Read bytes
        for k in range(2):
            x = bus.read_byte_data(80, k)
            res.append(x)
        self.assertEqual(len(res), 2, msg="Result array of incorrect length.")

        # Read word
        x = bus.read_word_data(80, 0)
        res2.append(x & 255)
        res2.append(x / 256)
        self.assertEqual(len(res2), 2, msg="Result array of incorrect length.")
        self.assertListEqual(res, res2, msg="Byte and word reads differ")

        # Read block of N bytes
        n = 2
        x = bus.read_i2c_block_data(80, 0, n)
        res3.extend(x)
        self.assertEqual(len(res3), n, msg="Result array of incorrect length.")
        self.assertListEqual(res, res3, msg="Byte and block reads differ")

        bus.close()


class TestSMBusWrapper(unittest.TestCase):
    """Similar test as TestSMBus except it encapsulates it all access within "with" blocks."""

    def test_func(self):
        with SMBusWrapper(1) as bus:
            print("\nSupported I2C functionality: %x" % bus.funcs)

    def test_read(self):
        res = []
        res2 = []
        res3 = []

        # Read bytes
        with SMBusWrapper(1) as bus:
            for k in range(2):
                x = bus.read_byte_data(80, k)
                res.append(x)
        self.assertEqual(len(res), 2, msg="Result array of incorrect length.")

        # Read word
        with SMBusWrapper(1) as bus:
            x = bus.read_word_data(80, 0)
            res2.append(x & 255)
            res2.append(x / 256)
        self.assertEqual(len(res2), 2, msg="Result array of incorrect length.")
        self.assertListEqual(res, res2, msg="Byte and word reads differ")

        # Read block of N bytes
        n = 2
        with SMBusWrapper(1) as bus:
            x = bus.read_i2c_block_data(80, 0, n)
            res3.extend(x)
        self.assertEqual(len(res3), n, msg="Result array of incorrect length.")
        self.assertListEqual(res, res3, msg="Byte and block reads differ")
