Tips and Tricks
===============

Community-sourced recipes for common tasks. Many of these originate from questions
raised in the issue tracker.

.. _signed-integer-conversion:

Signed Integer Conversion
--------------------------

smbus2 always returns **unsigned** integer values, matching the raw bytes from the bus.
To interpret a value as a signed integer, use Python's ``ctypes``
(`#11 <https://github.com/kplindegaard/smbus2/issues/11>`_):

.. code-block:: python

   from ctypes import c_int8, c_uint8, c_int16, c_uint16
   from smbus2 import SMBus

   with SMBus(1) as bus:
       # Read an unsigned byte and convert to signed
       unsigned_byte = bus.read_byte_data(0x50, 0x00)  # e.g. 200
       signed_byte = c_int8(unsigned_byte).value         # → -56

       # Convert a signed Python integer to the unsigned byte value sent on the wire
       signed_value = -123
       bus.write_byte_data(0x50, 0x00, c_uint8(signed_value).value)  # writes 133

       # Same pattern for 16-bit words
       unsigned_word = bus.read_word_data(0x50, 0x02)
       signed_word = c_int16(unsigned_word).value

.. _endianness-byte-order-conversion:

Endianness / Byte-Order Conversion
------------------------------------

``read_word_data`` returns a 16-bit integer assembled by the Linux kernel following the
SMBus convention (low byte first). If your device sends the high byte first (big-endian),
swap the bytes manually
(`#86 <https://github.com/kplindegaard/smbus2/issues/86>`_):

.. code-block:: python

   # Bit-manipulation swap
   value = bus.read_word_data(0x50, 0x00)
   swapped = ((value & 0xFF) << 8) | ((value >> 8) & 0xFF)

   # Alternatively, use the struct module
   import struct
   raw = bus.read_word_data(0x50, 0x00)
   (big_endian_value,) = struct.unpack('>H', struct.pack('<H', raw))

.. _reading-devices-that-have-no-register-address:

Reading Devices That Have No Register Address
----------------------------------------------

Devices like some ADCs, sensors, and actuators do not use the SMBus register-addressing
convention. The ``*_data`` family of functions **always prepend a register/offset write**,
which confuses these devices or triggers an error
(`#19 <https://github.com/kplindegaard/smbus2/issues/19>`_,
`#84 <https://github.com/kplindegaard/smbus2/issues/84>`_,
`#117 <https://github.com/kplindegaard/smbus2/issues/117>`_).

Use ``i2c_rdwr`` with a bare ``i2c_msg`` instead:

.. code-block:: python

   from smbus2 import SMBus, i2c_msg

   with SMBus(1) as bus:
       msg = i2c_msg.read(0x40, 2)   # read 2 bytes — no register byte sent
       bus.i2c_rdwr(msg)
       data = list(msg)
       print(data)

For a single-byte write without a register:

.. code-block:: python

   with SMBus(1) as bus:
       bus.write_byte(0x40, 0x8C)    # write_byte sends only the data byte

.. _write-then-read-repeated-start:

Write-Then-Read (Repeated Start)
----------------------------------

Many sensors require you to write a command or register-select byte and then read the
response **without a STOP condition** (repeated start) in between. Use dual ``i2c_rdwr``
(`#25 <https://github.com/kplindegaard/smbus2/issues/25>`_):

.. code-block:: python

   from smbus2 import SMBus, i2c_msg

   addr = 0x50
   command = 0xAC

   with SMBus(1) as bus:
       write = i2c_msg.write(addr, [command])
       read  = i2c_msg.read(addr, 6)
       bus.i2c_rdwr(write, read)     # single ioctl — repeated start between messages
       data = list(read)
       print(data)

Checking Adapter Capabilities
-------------------------------

Use ``bus.funcs`` and the ``I2cFunc`` IntFlag to query what the adapter supports
(`#64 <https://github.com/kplindegaard/smbus2/issues/64>`_):

.. code-block:: python

   import smbus2

   with smbus2.SMBus(1) as bus:
       funcs = bus.funcs
       if funcs & smbus2.I2cFunc.I2C:
           print("Raw I2C (i2c_rdwr) is supported")
       if funcs & smbus2.I2cFunc.ADDR_10BIT:
           print("10-bit addressing is supported")
       if funcs & smbus2.I2cFunc.SMBUS_PEC:
           print("Packet Error Checking (PEC) is supported")

Sharing the Bus Across Multiple Modules
-----------------------------------------

Avoid creating more than one ``SMBus`` object for the same physical bus in a single
process (`#75 <https://github.com/kplindegaard/smbus2/issues/75>`_). A simple singleton
pattern ensures only one instance exists:

.. code-block:: python

   import atexit
   from smbus2 import SMBus

   class _BusHolder:
       _instance = None

       def __new__(cls):
           if cls._instance is None:
               cls._instance = SMBus(1)
               atexit.register(cls._instance.close)
           return cls._instance

   def get_bus() -> SMBus:
       """Return the shared SMBus instance."""
       return _BusHolder()

For multi-threaded code, add a ``threading.Lock`` around each operation — see
:doc:`best_practices` for an example.

.. _asyncio-async-support:

asyncio / Async Support
------------------------

smbus2 itself is **synchronous**. For ``asyncio`` applications, a community library
wraps smbus2 with async/await support
(`#18 <https://github.com/kplindegaard/smbus2/issues/18>`_):

- **smbus2_asyncio** — https://github.com/jabdoa2/smbus2_asyncio (Python 3.4+)

Note that because I2C operations are typically short and infrequent, running them in a
thread pool executor (``asyncio.get_event_loop().run_in_executor``) is often sufficient
without a dedicated async library:

.. code-block:: python

   import asyncio
   from smbus2 import SMBus

   async def read_sensor():
       loop = asyncio.get_event_loop()
       with SMBus(1) as bus:
           value = await loop.run_in_executor(
               None, bus.read_byte_data, 0x50, 0x00
           )
       return value

.. _setting-i2c-bus-clock-speed-baud-rate:

Setting I2C Bus Clock Speed (Baud Rate)
-----------------------------------------

smbus2 does **not** expose a clock-speed setting
(`#77 <https://github.com/kplindegaard/smbus2/issues/77>`_).
The I2C clock is controlled at the kernel/hardware level:

- **Raspberry Pi** — add ``dtparam=i2c_arm_baudrate=100000`` to ``/boot/config.txt``
  (replaces ``i2c_arm`` overlay parameter).
- **Other SBCs** — consult the board's device-tree documentation.
- **Kernel module parameter** — some drivers accept a ``baudrate`` or ``speed`` parameter
  via ``modprobe``.

Clock stretching (the slave holding SCL low to pause the master) is also handled
entirely by the kernel driver.

Opening a Bus by File Path
---------------------------

Since v0.3.0 you can open a bus by its ``/dev`` path instead of its integer index
(`#17 <https://github.com/kplindegaard/smbus2/issues/17>`_):

.. code-block:: python

   from smbus2 import SMBus

   bus = SMBus('/dev/i2c-3')   # equivalent to SMBus(3)

This is useful when the bus index changes across reboots or when the device path is
determined at runtime.
