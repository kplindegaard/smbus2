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

from smbus2.smbus2 import i2c_smbus_ioctl_data, union_i2c_smbus_data, union_pointer_type
from smbus2.smbus2 import I2C_SMBUS_BLOCK_MAX, I2C_SMBUS_READ, I2C_SMBUS_BYTE_DATA
import unittest



class TestDataTypes(unittest.TestCase):

    def test_union_i2c_smbus_data(self):
        u = union_i2c_smbus_data()

        # Fill array with values 1, 2, ...
        for k in range(I2C_SMBUS_BLOCK_MAX+2):
            u.block[k] = k+1

        # Check that the union works
        self.assertEqual(u.byte, u.block[0], msg="Byte field differ")
        self.assertEqual(u.block[16], 17, msg="Array field does not match")

        # Set byte and se it reflected in the array
        u.byte = 255
        self.assertEqual(u.block[0], 255, msg="Byte field not reflected in array")

        # Reset array to zeros and check word field
        for k in range(I2C_SMBUS_BLOCK_MAX+2):
            u.block[k] = 0
        u.word = 1607
        self.assertNotEqual(0, u.word, msg="Word field is zero but should be non-zero")
        u.word = 0

    def test_ioctl_data_factory(self):
        ioctl_msg = i2c_smbus_ioctl_data.create()

        self.assertEqual(ioctl_msg.read_write, I2C_SMBUS_READ)
        self.assertEqual(ioctl_msg.size, I2C_SMBUS_BYTE_DATA)

        # Simple test to check assignment
        ioctl_msg.data.contents.byte = 25
        self.assertEqual(ioctl_msg.data.contents.byte, 25, msg="Get not equal to set")

